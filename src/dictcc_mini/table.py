from shutil import get_terminal_size
from itertools import zip_longest
from dictcc_mini.config import FIELD_STYLES, FIELD_DEFAULT, \
                               INLINE_STYLES, INLINE_DEFAULT
from dictcc_mini.misc import partition_to_column, next_head, visual_length

class Entry:
    def __init__(self, content: str):
        self.content: str = content

    def __contains__(self, string):
        return string in self.content
    def __len__(self):
        return max(visual_length(part) for part in self.partial_content)

    @property
    def is_multiline(self):
        return '\n' in self
    @property
    def partial_content(self):
        return self.content.split('\n') if self.is_multiline else [self.content]

    def adjust_for_col_width(self, col_width_thresh):
        field_ind0, field_ind1, field_ind2 = FIELD_STYLES[FIELD_DEFAULT]
        lines = []
        while True:
            is_first_line = (len(lines) == 0)
            current_indicator = field_ind0 if is_first_line else field_ind1
            available_width = col_width_thresh - len(current_indicator)
            if len(self) <= available_width: # last line!
                break
            head, self.content = next_head(self.content, available_width)
            lines.append(f'{current_indicator}{head}')
        last_indicator = field_ind0 if not lines else field_ind2
        lines.append(f'{last_indicator}{self.content}')
        self.content = "\n".join(lines)

class Column:
    def __init__(self, entries: list[str], table_length: int) -> None:
        self.entries = [Entry(content) for content in entries[ : table_length]]

    @property
    def contents(self):
        return [entry.content for entry in self.entries]
    @property
    def longest_entry(self) -> int:
        return max(len(entry) for entry in self.entries)

    def preprocess(self, col_width_thresh: int) -> None:
        for entry in self.entries:
            if len(entry) > col_width_thresh:
                entry.adjust_for_col_width(col_width_thresh)

class Table:
    def __init__(self, entries_left, entries_right,
                 table_length, terminal_width: None | int = None) -> None:
        self.table_length = table_length
        self.terminal_width = terminal_width if terminal_width else \
                              get_terminal_size()[0]
        self.center_pad = INLINE_STYLES[INLINE_DEFAULT]
        self.pad_right_of_placeholders = ''     # not in use yet maybe usefull
        self.pad_left_of_placeholders = ''      # in a future version
        self.left_column = Column(entries_left, self.table_length)
        self.right_column = Column(entries_right, self.table_length)
        width_left, width_right = self.negotiate_widths()
        self.left_column.preprocess(width_left)
        self.right_column.preprocess(width_right)
        # these two can only be determined after negotiate_widths as they
        # depend on where lines have been broken.
        self.warn_terminal_width()
        self.longest_l = self.left_column.longest_entry

    def __str__(self) -> str:
        pairs = list(zip(self.left_column.entries, self.right_column.entries))
        return ''.join(f'{self.format_entry_pair(*pair)}'
                         for pair in pairs[ : self.table_length]).strip()
    def show(self) -> None:
        print(self)

    @property
    def total_width_for_columns(self):
        return self.terminal_width - len(self.center_pad)

    def warn_terminal_width(self):
        WARN_THRESH = self.left_column.longest_entry + \
                      self.right_column.longest_entry + len(self.center_pad)
        if WARN_THRESH > self.terminal_width:
            msg = f'Terminal very small: {self.terminal_width} columns. ' \
                  f'Expect tearing.'
            print(f'{partition_to_column(msg, self.terminal_width)}\n')

    def negotiate_widths(self) -> tuple[int, int]:
        max_l = self.left_column.longest_entry
        max_r = self.right_column.longest_entry
        available_total = self.total_width_for_columns
        if max_l + max_r <= available_total:
            return max_l, max_r
        fair_share = available_total // 2
        if max_l <= fair_share:
            target_left_col, target_right_col = max_l, available_total - max_l
        elif max_r <= fair_share:
            target_left_col, target_right_col = available_total - max_r, max_r
        else:
            target_left_col = target_right_col = fair_share
        width_left = available_total - target_right_col
        width_right = available_total - target_left_col
        return width_left, width_right

    def len_place_holders(self, left: str) -> int:
        return self.longest_l - visual_length(left)

    def left_with_place_holders(self, left: str, first: bool = True) -> str:
        inline_pad = self.center_pad if first else ' ' * len(self.center_pad)
        # evens out central padding on the left edge with spaces
        rest = self.len_place_holders(left) % len(inline_pad)
        left = f'{left}{' ' * rest}'
        how_many_pads = self.len_place_holders(left) // len(inline_pad) + 1
        return f'{left}{self.pad_left_of_placeholders}' \
               f'{inline_pad * how_many_pads}{self.pad_right_of_placeholders}'

    def format_entry_pair(self, left: Entry, right: Entry) -> str:
        res = ''
        pairs = zip_longest(left.partial_content, right.partial_content)
        for i, (l, r) in enumerate(pairs):
            if i == 0:      # edge case for first line
                res += f'{self.left_with_place_holders(l)}{r}'
            elif l:
                if r:       # L+R available
                    res += f'\n{self.left_with_place_holders(l, first = False)}{r}'
                else:       # only L available: exit loop
                    res += f"\n{l}"
            elif r:           # only R available: exit loop
                left_pad_factor = self.longest_l + len(self.center_pad) + \
                        len(self.pad_left_of_placeholders) + \
                        len(self.pad_right_of_placeholders)
                res += f'\n{left_pad_factor * ' '}{r}'
        return f'{res}\n'
