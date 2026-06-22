#!/usr/bin/python3.15

import json
import os
from time import sleep
from dictcc_mini.scraper import scrape_for_content, parse_content

def save_raw_html(file_path, word, languages='deen'):
    content = scrape_for_content(word, languages)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Saved to {file_path}')

def dump_sample_columns(file_path, table_length):
    with open(f'{file_path.replace('json', 'html')}', 'r', encoding='utf-8') as f:
        left, right = parse_content(f.read(), table_length)
    sample = {
        "word": word,
        "left": left,
        "right": right
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=4, ensure_ascii=False)
    print(f"Saved to {file_path}")

if __name__ == "__main__":
    test_terms = {'DEEN': ['was', 'kanzler', 'bremsstrahlung', 'hi', 'test'],
                  'DERU': ['pferd']}
    table_length = 1000
    try:
        p = f'{os.getenv('DICTCC_BASE')}/test/data/'
    except Exception as e:
        print(f'Something went wrong:  {e}')
    os.makedirs(name=p, exist_ok=True)
    for lang_pair, words in test_terms.items():
        for word in words:
            save_raw_html(f'{p}{word}.html', word, languages=lang_pair)
            dump_sample_columns(f'{p}{word}.json', table_length)
            sleep(1)
