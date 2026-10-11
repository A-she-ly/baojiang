import json

with open('src/data/LCDP_S1E01_cards.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for card in data:
    if card['id'] == 'LCDP_S1E01_078':
        old_note = card['cultural_note']
        # Fix comenzar IPA: /ko.men.ˈsaɾ/ → /ko.men.ˈθaɾ/ (z → /θ/ in Castilian)
        old_note = old_note.replace('/ko.men.ˈsaɾ/', '/ko.men.ˈθaɾ/')
        # Fix historia IPA: /is.ˈto.ja/ → /is.ˈtoɾ.ja/ (r → /ɾ/)
        old_note = old_note.replace('/is.ˈto.ja/', '/is.ˈtoɾ.ja/')
        card['cultural_note'] = old_note
        break

with open('src/data/LCDP_S1E01_cards.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done!')
