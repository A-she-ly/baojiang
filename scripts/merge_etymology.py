"""
将 new_etymology_entries.py 中的词源学数据合并到 LCDP S3E01 名词闪卡 JSON 中
"""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 导入新词源条目
sys.path.insert(0, 'scripts')
from new_etymology_entries import NEW_ETYMOLOGY_ENTRIES

DATA_FILE = 'src/data/LCDP_S3E01_nouns_cards.json'

# 读取现有卡片
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    cards = json.load(f)

total = len(cards)
missing_before = sum(1 for c in cards if not c.get('etymology'))
updated = 0
skipped = 0

for card in cards:
    word = card['target_word'].lower()
    if not card.get('etymology') and word in NEW_ETYMOLOGY_ENTRIES:
        entry = NEW_ETYMOLOGY_ENTRIES[word]
        card['etymology'] = entry['breakdown']
        updated += 1
    elif not card.get('etymology'):
        skipped += 1

missing_after = sum(1 for c in cards if not c.get('etymology'))

# 写回文件
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Total cards: {total}")
print(f"Missing before: {missing_before}")
print(f"Updated: {updated}")
print(f"Still missing: {missing_after}")
print(f"Skipped (no entry): {skipped}")
print(f"Coverage: {(total - missing_after)}/{total} ({100*(total-missing_after)/total:.1f}%)")
