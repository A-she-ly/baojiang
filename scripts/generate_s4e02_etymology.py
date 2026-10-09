"""
Generate etymology for S4E02 cards using pattern-based Spanish etymology rules.
"""
import json
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'scripts')
from spanish_etymology import ETYMOLOGY_DICT

with open('src/data/LCDP_S4E02_cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

def generate_etymology(word, pos_tag):
    """Generate etymology breakdown based on Spanish word patterns."""
    w = word.lower()
    
    # Check existing dictionary first
    if w in ETYMOLOGY_DICT:
        return ETYMOLOGY_DICT[w]['breakdown']
    
    # Normalize: strip accents for pattern matching (data may lack accent marks)
    import unicodedata
    w_norm = unicodedata.normalize('NFKD', w).encode('ASCII', 'ignore').decode('ASCII')
    
    # Pattern-based generation
    breakdown = []
    
    if pos_tag.startswith('v.'):
        # Verbs: stem + infinitive ending
        if w.endswith('ar'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ar", "origin": "拉丁语 -āre", "meaning": "第一变位动词后缀"})
        elif w.endswith('er'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-er", "origin": "拉丁语 -ēre", "meaning": "第二变位动词后缀"})
        elif w.endswith('ir'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ir", "origin": "拉丁语 -īre", "meaning": "第三变位动词后缀"})
        
        # Handle prefixes
        if w.startswith('a') and len(w) > 4:
            breakdown[0]['origin'] = '拉丁语词根'
            breakdown[0]['meaning'] = '词干（可能含前缀 a-）'
        elif w.startswith('re') and len(w) > 5:
            breakdown[0]['origin'] = '拉丁语词根（re- 重新）'
            breakdown[0]['meaning'] = '词干（含前缀 re-）'
        elif w.startswith('de') and len(w) > 5:
            breakdown[0]['origin'] = '拉丁语词根（de- 向下/离开）'
            breakdown[0]['meaning'] = '词干（含前缀 de-）'
        elif w.startswith('ex') and len(w) > 5:
            breakdown[0]['origin'] = '拉丁语词根（ex- 向外）'
            breakdown[0]['meaning'] = '词干（含前缀 ex-）'
        elif w.startswith('con') and len(w) > 6:
            breakdown[0]['origin'] = '拉丁语词根（con- 共同）'
            breakdown[0]['meaning'] = '词干（含前缀 con-）'
        elif w.startswith('in') and len(w) > 5:
            breakdown[0]['origin'] = '拉丁语词根（in- 进入/否定）'
            breakdown[0]['meaning'] = '词干（含前缀 in-）'
    
    elif pos_tag.startswith('n.'):
        # Nouns: stem + gender suffix
        # Handle plural first
        is_plural = False
        base = w
        base_norm = w_norm
        if w_norm.endswith('es') and len(w_norm) > 3:
            is_plural = True
            base = w[:-2]  # remove -es
            base_norm = w_norm[:-2]
        elif w_norm.endswith('s') and len(w_norm) > 2:
            is_plural = True
            base = w[:-1]  # remove -s
            base_norm = w_norm[:-1]
        
        if base_norm.endswith('cion') or base_norm.endswith('sion'):
            suffix = base[-4:] if len(base) >= 4 else base
            stem = base[:-4] if len(base) >= 4 else ''
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": f"-{suffix}", "origin": "拉丁语 -tiōnem / -siōnem", "meaning": "动作/状态名词后缀"})
        elif base_norm.endswith('dad') or base_norm.endswith('tad'):
            suffix = base[-3:]
            stem = base[:-3]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": f"-{suffix}", "origin": "拉丁语 -tātem", "meaning": "抽象名词后缀"})
        elif base_norm.endswith('miento'):
            stem = base[:-6]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-miento", "origin": "拉丁语 -mentum", "meaning": "动作结果名词后缀"})
        elif base_norm.endswith('aje'):
            stem = base[:-3]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-aje", "origin": "法语 -age / 拉丁语 -aticum", "meaning": "集合/动作名词后缀"})
        elif base_norm.endswith('ero') or base_norm.endswith('era'):
            stem = base[:-3]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ero/-era", "origin": "拉丁语 -arius", "meaning": "职业/工具/地点后缀"})
        elif base_norm.endswith('ista'):
            stem = base[:-4]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ista", "origin": "希腊语 -ιστής", "meaning": "从事...的人"})
        elif base_norm.endswith('al'):
            stem = base[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-al", "origin": "拉丁语 -ālis", "meaning": "与...相关的"})
        elif base_norm.endswith('or'):
            stem = base[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-or", "origin": "拉丁语 -or", "meaning": "抽象名词/施事者后缀"})
        elif base_norm.endswith('on'):
            stem = base[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ón", "origin": "增大后缀", "meaning": "增大/强调"})
        elif base_norm.endswith('an') or base_norm.endswith('en') or base_norm.endswith('in') or base_norm.endswith('un'):
            stem = base[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": f"-{base[-2:]}", "origin": "重音名词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('o'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-o", "origin": "西班牙语阳性名词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('a'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-a", "origin": "西班牙语阴性名词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('e'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-e", "origin": "名词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('l'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-l", "origin": "拉丁语 -lis", "meaning": "名词标记"})
        elif base_norm.endswith('z'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-z", "origin": "名词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('u'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-u", "origin": "拉丁语 -us", "meaning": "名词标记"})
        elif base_norm.endswith('i'):
            stem = base[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-i", "origin": "外来词后缀", "meaning": "名词标记"})
        elif base_norm.endswith('er'):
            stem = base[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-er", "origin": "外来词后缀", "meaning": "名词标记"})
        else:
            breakdown.append({"part": base, "origin": "词根", "meaning": "完整词形"})
        
        if is_plural:
            breakdown.append({"part": "-s/-es", "origin": "复数标记", "meaning": "西班牙语复数后缀"})
    
    elif pos_tag.startswith('adj'):
        # Adjectives
        if w_norm.endswith('oso') or w_norm.endswith('osa'):
            stem = w[:-3]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-oso/-osa", "origin": "拉丁语 -ōsus", "meaning": "充满...的"})
        elif w_norm.endswith('able'):
            stem = w[:-4]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-able", "origin": "拉丁语 -abilis", "meaning": "能够...的"})
        elif w_norm.endswith('ivo') or w_norm.endswith('iva'):
            stem = w[:-3]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-ivo/-iva", "origin": "拉丁语 -īvus", "meaning": "具有...性质的"})
        elif w_norm.endswith('al'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-al", "origin": "拉丁语 -ālis", "meaning": "与...相关的"})
        elif w_norm.endswith('az'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-az", "origin": "拉丁语 -āx", "meaning": "倾向/性质形容词后缀"})
        elif w_norm.endswith('o'):
            stem = w[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-o", "origin": "西班牙语阳性形容词后缀", "meaning": "形容词标记"})
        elif w_norm.endswith('a'):
            stem = w[:-1]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-a", "origin": "西班牙语阴性形容词后缀", "meaning": "形容词标记"})
        elif w_norm.endswith('en'):
            stem = w[:-2]
            breakdown.append({"part": f"{stem}-", "origin": "词根", "meaning": "词干"})
            breakdown.append({"part": "-en", "origin": "形容词后缀", "meaning": "形容词标记"})
        else:
            breakdown.append({"part": w, "origin": "词根", "meaning": "完整词形"})
    
    elif pos_tag.startswith('adv'):
        breakdown.append({"part": w, "origin": "词根", "meaning": "完整词形"})
    
    return breakdown

# Add etymology to all cards
updated = 0
for card in cards:
    if not card.get('etymology'):
        etymology = generate_etymology(card['target_word'], card['pos'])
        card['etymology'] = etymology
        updated += 1

with open('src/data/LCDP_S4E02_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Updated {updated} cards with etymology data")

# Verify
no_etymology = [c for c in cards if not c.get('etymology')]
print(f"Cards without etymology: {len(no_etymology)}")
