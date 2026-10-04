import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/data/LCDP_S3E07_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

bad = [c for c in cards if c.get('sentence_cloze', '') == c.get('sentence_full', '')]
for c in bad:
    print(f"ID: {c['id']}")
    print(f"Target: {c['target_word']}")
    print(f"POS: {c['pos']}")
    print(f"Sentence: {c['sentence_full']}")
    print(f"Translation: {c.get('sentence_translation', '')}")
