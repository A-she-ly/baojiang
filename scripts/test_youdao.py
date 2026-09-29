import asyncio
import aiohttp
import json

async def test_youdao():
    async with aiohttp.ClientSession() as s:
        # Try Youdao free translation
        url = 'https://fanyi.youdao.com/translate'
        data = {
            'i': 'And hey, you need anything, you can always come to Joey.',
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }
        async with s.post(url, data=data, ssl=False) as r:
            text = await r.text()
            print("Status:", r.status)
            print("Response:", text[:500])

asyncio.run(test_youdao())
