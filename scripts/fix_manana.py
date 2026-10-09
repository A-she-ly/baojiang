import json
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

f = open('src/data/LCDP_S3E01_nouns_cards.json', 'r', encoding='utf-8')
cards = json.load(f)
f.close()

fixed = 0
for c in cards:
    if 'context_examples' in c:
        for ce in c['context_examples']:
            if ce['chinese'] == '如今 每天早上' and 'despertar' in ce['espanol']:
                ce['chinese'] = '如今，每天早上醒来时，'
                fixed += 1

f = open('src/data/LCDP_S3E01_nouns_cards.json', 'w', encoding='utf-8')
json.dump(cards, f, ensure_ascii=False, indent=2)
f.close()

print(f'Fixed {fixed} context example(s)')
