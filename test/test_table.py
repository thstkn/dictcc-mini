#!/usr/bin/python3.15

import json
from dictcc_mini.table import Table
from os.path import join
from os import listdir, getenv

#WIDTHS = [80, 40, 30, 20]
WIDTHS = [80, 20]
#WIDTHS = [80]
dictmini_path = getenv('DICTCC_BASE')
assert dictmini_path, 'Make sure `DICTCC_BASE` env var is set to correct path'
PATH = f'{dictmini_path}/test/data'
JSON_PATHS = [join(PATH, l) for l in listdir(PATH) if 'json' in l]

def test_rendering_logic(path: str):
    print(f'Testing:\t{path}')
    with open(path, "r") as f:
        data = json.load(f)

    for width in WIDTHS:
        print(f"width:\t\t{width}\tword:\t{data['word']}\n")
        table = Table(data['left'],
                      data['right'],
                      full_table=False,
                      terminal_width=width)
        table.show()
        print()

if __name__ == '__main__':
    for path in sorted(JSON_PATHS):
        #if not 'pferd' in path:
            #continue
        test_rendering_logic(path)
