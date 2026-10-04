import sys
import io
import json
import time
import urllib.request
import urllib.parse

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Script started", flush=True)

# Test API
url = "https://api.mymemory.translated.net/get?q=casa&langpair=es|zh-CN"
req = urllib.request.Request(url, headers={'User-Agent': 'test'})
print("Sending request...", flush=True)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
print(f"Translation: {data['responseData']['translatedText']}", flush=True)
print("Test passed!", flush=True)
