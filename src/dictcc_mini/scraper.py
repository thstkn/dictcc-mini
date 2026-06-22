from urllib.request import Request, urlopen
from urllib.parse import quote
from html.parser import HTMLParser
from dictcc_mini.config import DEFAULT_LANG_PAIR, DEFAULT_HEADERS

def scrape_for_content(word: str, languages) -> str | None:
    ''' Returns decoded html string '''
    url = get_url(word, languages)
    req = Request(url, headers=DEFAULT_HEADERS)
    try:
        with urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f'scrape_for_content: Error connecting to dict.cc: {e}')

def parse_content(content: str, table_length: int) -> tuple[list[str], list[str]]:
    parser = DictParser()
    parser.feed(content)
    entries_left, entries_right = parser.data[0::2], parser.data[1::2]
    return entries_left[ : table_length], entries_right[ : table_length]

def get_url(word, langs=None) -> str:
    langs = langs if langs else DEFAULT_LANG_PAIR
    safe_word = quote(word)     # quote to make compatible with umlauts
    return f'https://{langs}.dict.cc/?s={safe_word}'

class DictParser(HTMLParser):
    def __init__(self, show_frequency=False):
        super().__init__()
        self.data = []
        self.show_frequency = show_frequency
        self.in_target_td = False       # contents
        self.in_gendatakk = False      # gendatakk
        self.in_dfn = False
        self.in_ignored_div = False
        self.main_buffer = []
        self.tag_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'td' and attrs_dict.get('class') == 'td7nl':
            self.in_target_td = True
        elif self.in_target_td:
            if tag == 'dfn':
                self.in_dfn = True
            elif tag == 'sup':
                self.in_gendatakk = True
            elif tag == 'div' and 'color:#999' in attrs_dict.get('style', ''):
                if not self.show_frequency:
                    self.in_ignored_div = True

    def handle_data(self, data):
        OPENERS = '(', '{', '[', '<', '/'
        CLOSERS = ')', '}', ']', '>', ',', '.', '!', '?', '/'
        if self.in_target_td and not self.in_ignored_div:
            if not (stripped := data.strip()):
                return
            if self.in_dfn:
                self.tag_buffer.append(f'[{stripped}]')
            elif self.in_gendatakk:
                self.main_buffer.append('{' + data.strip() + '}')

            elif self.main_buffer:
                last_item = self.main_buffer[-1]
                strippedswh = stripped.startswith('-')
                lastewh = last_item.endswith('-')
                strippedic = stripped in CLOSERS
                last_is_opener = any(last_item.endswith(o) for o in OPENERS)
                stripped_is_opener = any(stripped.startswith(o) for o in OPENERS)
                if strippedswh or \
                        strippedic or \
                        (lastewh and not stripped_is_opener) or \
                        last_is_opener:
                    self.main_buffer[-1] = last_item + stripped
                else:
                    self.main_buffer.append(stripped)
            else:
                self.main_buffer.append(stripped)

    def handle_endtag(self, tag):
        if tag == 'dfn':
            self.in_dfn = False
        elif tag == 'sup':
            self.in_gendatakk = False
        elif tag == 'div':
            self.in_ignored_div = False
        elif tag == 'td' and self.in_target_td:
            entry = " ".join(self.main_buffer)
            if self.tag_buffer:
                entry += " " + " ".join(self.tag_buffer)
            if (stripped := entry.strip()):
                self.data.append(stripped)
            self.main_buffer = []
            self.tag_buffer = []
            self.in_target_td = False
