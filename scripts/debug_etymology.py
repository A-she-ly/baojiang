import unicodedata
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

word = 'libertad'
w = word.lower()
w_norm = unicodedata.normalize('NFKD', w).encode('ASCII', 'ignore').decode('ASCII')
print(f"word: {word}")
print(f"w: {w}")
print(f"w_norm: {w_norm}")
print(f"endswith dad: {w_norm.endswith('dad')}")
print(f"len: {len(w_norm)}")

word2 = 'espiritu'
w2 = word2.lower()
w2_norm = unicodedata.normalize('NFKD', w2).encode('ASCII', 'ignore').decode('ASCII')
print(f"\nword: {word2}")
print(f"w_norm: {w2_norm}")
print(f"endswith u: {w2_norm.endswith('u')}")
