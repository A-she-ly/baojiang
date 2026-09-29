import json

cards = json.load(open('src/data/Friends_S01E01_nouns_cards.json', encoding='utf-8'))

# Collect all unique sentences
sentences = set()
for c in cards:
    sentences.add(c['sentence_full'])
    for ctx in c.get('context_examples', []):
        sentences.add(ctx['english'])

# Sort by length (shorter first, easier to translate)
sorted_s = sorted(sentences, key=len)

with open('scripts/sentences_to_translate.txt', 'w', encoding='utf-8') as f:
    for i, s in enumerate(sorted_s):
        f.write(f"{i+1}. {s}\n")

print(f"Total unique sentences: {len(sorted_s)}")
