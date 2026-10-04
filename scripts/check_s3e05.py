import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open('src/data/LCDP_S3E05_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)
print(f'Total: {len(cards)}')
no_cn = sum(1 for c in cards if not c.get('sentence_translation','').strip())
print(f'No Chinese translation: {no_cn}')
for c in cards[5:12]:
    print(f"{c['target_word']} ({c['tags'][0]}) | {c['translation']}")
    print(f"  ES: {c['sentence_full']}")
    print(f"  CN: {c['sentence_translation']}")
    print()
