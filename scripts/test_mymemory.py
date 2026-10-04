"""
Test MyMemory translation API (free, no key needed, 5000 words/day)
"""
import sys
import io
import urllib.request
import urllib.parse
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def translate_mymemory(text: str, source='es', target='zh-CN') -> str:
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={source}|{target}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data['responseData']['translatedText']


# Test
tests = ['abortar', 'casa', 'Hay que abortar.', 'El banco está cerrado.']
for t in tests:
    result = translate_mymemory(t)
    print(f"{t} -> {result}")
