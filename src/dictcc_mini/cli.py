from argparse import ArgumentParser
from shutil import get_terminal_size

from dictcc_mini.config import COUNTRY_CODES, DEFAULT_LANG1, DEFAULT_TABLE_LEN
from dictcc_mini.scraper import get_entries
from dictcc_mini.table import Table
from dictcc_mini.misc import partition_to_column

def parse():
    parser = ArgumentParser(prog='dictcc-mini',
                            description='Lightweight dictionary access.')
    parser.add_argument('word', type=str, help='lookup this word')
    parser.add_argument('-f', '--full', action='store_true', required=False,
                        help="don't shorten to 20 entries")
    parser.add_argument('-l', '--language', action='store_true', required=False,
                        help='start with language selector')
    return parser.parse_args()

def select_languages() -> str:
    country_codes = partition_to_column(' '.join(COUNTRY_CODES), get_terminal_size()[0])
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
    print(f'{msg}\n{res = }')
    return res

def main():
    ARGS = parse()
    lang_select = select_languages() if ARGS.language else None
    table_length = 1000 if ARGS.full else DEFAULT_TABLE_LEN
    left_entries, right_entries = get_entries(ARGS.word, lang_select, table_length)
    if not left_entries:
        print('No result')
        return
    else:
        Table(left_entries, right_entries, table_length).show()

if __name__ == '__main__':
    main()
