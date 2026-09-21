import json
data = json.load(open('src/data/S01E01_cards.json', encoding='utf-8'))
transcript = [c for c in data if not c.get('is_example_sentence')]
missing_sent = []
missing_prev = []
missing_next = []
for c in transcript:
    if not c.get('sentence_translation'):
        missing_sent.append((c['target_word'], c['sentence_full'][:80]))
    if c.get('context_prev') and not c.get('context_prev_cn'):
        missing_prev.append(c['context_prev'][:80])
    if c.get('context_next') and not c.get('context_next_cn'):
        missing_next.append(c['context_next'][:80])

print(f"Missing sentence_translation: {len(missing_sent)}")
for w, s in missing_sent:
    print(f"  [{w}] {s}")
print(f"\nMissing context_prev_cn: {len(missing_prev)}")
for s in set(missing_prev):
    print(f"  {s}")
print(f"\nMissing context_next_cn: {len(missing_next)}")
for s in set(missing_next):
    print(f"  {s}")
