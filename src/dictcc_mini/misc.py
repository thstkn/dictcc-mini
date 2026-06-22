from shutil import get_terminal_size

from dictcc_mini.config import COUNTRY_CODES, DEFAULT_LANG1, DEFAULT_LANG_PAIR

def visual_length(string: str) -> int:
    combining_accents = string.count('\u0301')
    return len(string) - combining_accents

def split_index(string: str, start, available_width, delim) -> int:
    split_index = string.rfind(delim, start, available_width)
    if split_index == -1:
        split_index = string.find(delim, available_width)
        if split_index == -1:
            split_index = available_width
    return split_index

def next_head(long_str: str, columns: int) -> tuple[str, str]:
    index = split_index(long_str, 0, columns, ' ')
    head = long_str[ : index ].rstrip()
    remains = long_str[ index : ].lstrip()
    return head, remains

def partition_to_column(long_str: str, columns: int) -> str:
    if len(long_str) <= columns:
        return long_str
    head, remains = next_head(long_str, columns)
    if len(remains) <= columns:
        return f'{head}\n{remains}'
    else:
        return f'{head}\n{partition_to_column(remains, columns)}'

def select_languages(start_selector: bool = False) -> str:
    if not start_selector:
        return DEFAULT_LANG_PAIR
    country_codes = partition_to_column(
            ' '.join(COUNTRY_CODES), get_terminal_size()[0])
    print(f'{country_codes}')
    user_inputs = ['', '']
    msg = ''
    while not all(i.upper() in COUNTRY_CODES for i in user_inputs):
        raw_in = input('Enter country code(s): ')
        if len(raw_in) > 4:
            try:
                in1, in2 = raw_in.split()
            except Exception as e:
                continue
        elif any(len(raw_in) == num for num in (2,4)):
            in1, in2 = raw_in[:2], raw_in[2:]
        else:
            continue
        user_inputs = [in1, in2]
        for i, user_input in enumerate(user_inputs):
            if user_input.upper() not in COUNTRY_CODES:
                if i >= 1 and user_input == '':
                    msg = f"Defaulting to '{DEFAULT_LANG1.upper()}'\n"
                    user_inputs[1] = DEFAULT_LANG1
                else:
                    msg = f'Invalid language selector: {user_input}'
    res = ''.join(user_inputs)
    print(f'{msg}')
    return res

