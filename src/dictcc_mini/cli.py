from argparse import ArgumentParser

from dictcc_mini.config import DEFAULT_TABLE_LEN
from dictcc_mini.scraper import scrape_for_content, parse_content
from dictcc_mini.table import Table
from dictcc_mini.misc import select_languages

def parse():
    parser = ArgumentParser(prog='dictcc-mini',
                            description='Lightweight dictionary access.')
    parser.add_argument('word', type=str, help='lookup this word')
    parser.add_argument('-f', '--full', action='store_true', required=False,
                        help=f"don't shorten to {DEFAULT_TABLE_LEN} entries")
    parser.add_argument('-l', '--language', action='store_true', required=False,
                        help='start with language selector')
    return parser.parse_args()

def main():
    ARGS = parse()
    lang_select = select_languages(ARGS.language)
    content = scrape_for_content(ARGS.word, lang_select)
    if not content:
        raise ValueError(f'Got no content from scraping!')
    # used by both: parse_content and Table - needed for integration testing
    table_length = 1000 if ARGS.full else DEFAULT_TABLE_LEN
    left_entries, right_entries = parse_content(content, table_length)
    if not left_entries:
        print('No result')
        return
    else:
        Table(left_entries, right_entries, table_length).show()

if __name__ == '__main__':
    main()
