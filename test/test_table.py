#!/usr/bin/python3.15

import json
from os.path import join
from os import listdir, getenv
from shutil import get_terminal_size
from dictcc_mini.table import Table

#WIDTHS = [80, 40, 30, 20]
#WIDTHS = [80, 20]
#WIDTHS = [80, get_terminal_size()[0]]
#WIDTHS = [get_terminal_size()[0]]
WIDTHS = [get_terminal_size()[0], 40]
#WIDTHS = [80]
dictmini_path = getenv('DICTCC_BASE')
TLGS = [20]
assert dictmini_path, 'Make sure `DICTCC_BASE` env var is set to correct path'
PATH = f'{dictmini_path}/test/data'
JSON_PATHS = [join(PATH, l) for i, l in enumerate(listdir(PATH))
              if 'json' in l and i < 1e3]

def test_rendering_logic(path: str):
    print(f'Testing:\t{path}')
    with open(path, "r") as f:
        data = json.load(f)

    for width in WIDTHS:
        for table_length in TLGS:
            print(f"width:\t\t{width}\tword:\t{data['word']}\n")
            table = Table(data['left'],
                          data['right'],
                          table_length=table_length,
                          terminal_width=width)
            table.show()
            print()

if __name__ == '__main__':
    for path in sorted(JSON_PATHS):
        #if not 'pferd' in path:
            #continue
        test_rendering_logic(path)
