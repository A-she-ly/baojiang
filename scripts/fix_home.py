with open('src/components/Home.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove character, scene, level, and tags lines
lines_to_remove = [
    "    { key: 'character', i18nKey: 'home.filterCharacter', icon: '🎭' },\n",
    "    { key: 'scene', i18nKey: 'home.filterScene', icon: '🎬' },\n",
    "    { key: 'level', i18nKey: 'home.filterLevel', icon: '📶' },\n",
    "    { key: 'tags', i18nKey: 'home.filterTags', icon: '️' },\n",
]

for line in lines_to_remove:
    content = content.replace(line, '')

with open('src/components/Home.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
