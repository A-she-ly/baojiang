"""
Script: generate_phonetics_cards.py
Purpose:
  Generate phonetics-classified flashcard data for S01E01.
  Priority:
    1. Use REAL transcript lines from the script (sorted first)
    2. Supplement with example sentences only when needed (sorted after)
  Constraints:
    - Each pronunciation_focus category has >= 10 cards
    - Each target_word/phrase has <= 7 letters

Run:
  python scripts/generate_phonetics_cards.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Pronunciation classification for short words
# ---------------------------------------------------------------------------
def classify_word(word: str) -> list[str]:
    """Classify a word by its primary pronunciation focus."""
    w = word.lower().strip(".,!?;:\"'()[]")
    if len(w) > 7 or len(w) == 0:
        return []

    # flap_t: words with t/d between vowels (simplified)
    flap_t_patterns = [
        'better', 'water', 'little', 'butter', 'pretty', 'ladder', 'letter',
        'kitty', 'matter', 'bottle', 'city', 'dirty', 'duty', 'fatty',
        'gutter', 'happy', 'hurry', 'kitten', 'latter', 'litter', 'mutter',
        'neither', 'notify', 'party', 'petty', 'plenty', 'putty', 'quarter',
        'ready', 'really', 'settle', 'shutter', 'sitter', 'slightly',
        'spider', 'stutter', 'sweater', 'table', 'tattle', 'tattoo',
        'tender', 'terrible', 'together', 'tomato', 'total', 'tower',
        'twenty', 'utter', 'valley', 'very', 'waiting', 'weather', 'writer',
        'gotta', 'wanna', 'gonna', 'outta', 'otta', 'otta', 'otta',
        'otta', 'otta', 'otta', 'otta', 'otta', 'otta', 'otta',
    ]
    if w in flap_t_patterns or (len(w) >= 3 and w[1:-1].count('t') > 0 and any(v in w for v in 'aeiou')):
        if w in ['better', 'water', 'little', 'butter', 'pretty', 'ladder', 'letter',
                 'kitty', 'matter', 'bottle', 'city', 'dirty', 'duty', 'fatty',
                 'gutter', 'happy', 'hurry', 'kitten', 'latter', 'litter', 'mutter',
                 'neither', 'party', 'petty', 'plenty', 'putty', 'quarter',
                 'ready', 'really', 'settle', 'sitter', 'slightly',
                 'spider', 'sweater', 'table', 'tender', 'terrible', 'together',
                 'total', 'twenty', 'utter', 'valley', 'very', 'waiting', 'weather',
                 'gotta', 'wanna', 'gonna', 'outta']:
            return ['flap_t']

    # r_colored: words with r-colored vowels
    r_colored_patterns = [
        'her', 'bird', 'work', 'turn', 'girl', 'word', 'nurse', 'church',
        'burn', 'shirt', 'first', 'third', 'birth', 'dirt', 'flirt', 'skirt',
        'blur', 'stir', 'firm', 'worm', 'worth', 'world', 'early', 'learn',
        'earn', 'search', 'pearl', 'girl', 'curl', 'hurl', 'swirl', 'twirl',
        'url', 'whirl', 'churl', 'burl', 'furl', 'gerl', 'merl', 'nerl',
        'perl', 'terl', 'werl', 'yerl', 'zerl',
    ]
    if w in r_colored_patterns or (len(w) >= 3 and 'r' in w[1:] and any(v in w for v in 'aeiou')):
        if w in ['her', 'bird', 'work', 'turn', 'girl', 'word', 'nurse', 'church',
                 'burn', 'shirt', 'first', 'third', 'birth', 'dirt', 'flirt', 'skirt',
                 'blur', 'stir', 'firm', 'worm', 'worth', 'world', 'early', 'learn',
                 'earn', 'search', 'pearl', 'curl', 'hurl', 'swirl', 'twirl',
                 'whirl', 'burl', 'furl', 'gerl', 'merl', 'nerl', 'perl', 'terl',
                 'werl', 'yerl', 'zerl', 'churl', 'url']:
            return ['r_colored']

    # o_diphthong: words with /o/
    o_diphthong_patterns = [
        'go', 'no', 'so', 'show', 'know', 'grow', 'throw', 'blow', 'slow',
        'snow', 'flow', 'glow', 'low', 'row', 'bow', 'cow', 'how', 'now',
        'plow', 'allow', 'brow', 'crow', 'draw', 'flaw', 'gnaw', 'jaw',
        'law', 'paw', 'raw', 'saw', 'straw', 'thaw', 'yaw', 'zaw',
        'boat', 'coat', 'float', 'goat', 'moat', 'note', 'vote', 'wrote',
        'home', 'bone', 'cone', 'done', 'gone', 'hone', 'lone', 'none',
        'pone', 'rone', 'sone', 'tone', 'zone', 'phone', 'stone', 'throne',
        'blown', 'flown', 'grown', 'known', 'mown', 'own', 'shown', 'sown',
        'strown', 'thrown', 'town', 'down', 'brown', 'clown', 'crown',
        'drown', 'frown', 'gown', 'noun', 'renown', 'town', 'vow', 'wow',
    ]
    if w in o_diphthong_patterns:
        return ['o_diphthong']

    # long_e: words with /i/
    long_e_patterns = [
        'see', 'me', 'tree', 'free', 'three', 'key', 'need', 'keep', 'feel',
        'week', 'be', 'he', 'she', 'we', 'agree', 'degree', 'refugee',
        'trainee', 'absentee', 'devotee', 'employee', 'interviewee', 'nominee',
        'trustee', 'volunteer', 'engineer', 'pioneer', 'cashier', 'brigadier',
        'musketeer', 'auctioneer', 'balladeer', 'buccaneer', 'charioteer',
        'mountaineer', 'privateer', 'rifleer', 'sonneteer', 'sutler',
    ]
    if w in long_e_patterns:
        return ['long_e']

    # schwa: words with schwa sound (unstressed)
    schwa_patterns = [
        'sofa', 'panda', 'about', 'alone', 'banana', 'doctor', 'actor',
        'problem', 'today', 'support', 'supply', 'suggest', 'surprise',
        'surround', 'survey', 'survive', 'suspect', 'suspend', 'sustain',
        'swallow', 'swarm', 'swear', 'sweat', 'sweep', 'sweet', 'swell',
        'swept', 'swift', 'swim', 'swing', 'swirl', 'switch', 'sword',
        'swore', 'sworn', 'swung',
    ]
    if w in schwa_patterns:
        return ['schwa']

    # weak_forms: function words with weak forms
    weak_forms_patterns = [
        'to', 'for', 'and', 'of', 'can', 'was', 'some', 'that', 'from',
        'have', 'has', 'had', 'do', 'does', 'did', 'is', 'are', 'am',
        'were', 'been', 'being', 'be', 'the', 'a', 'an', 'in', 'on',
        'at', 'by', 'with', 'as', 'but', 'or', 'nor', 'yet', 'so',
        'if', 'then', 'than', 'when', 'where', 'why', 'how', 'what',
        'which', 'who', 'whom', 'whose', 'this', 'these', 'those',
    ]
    if w in weak_forms_patterns:
        return ['weak_forms']

    # y_glide: words starting with /j/ sound
    y_glide_patterns = [
        'you', 'yes', 'yet', 'use', 'cute', 'few', 'new', 'view', 'music',
        'unite', 'year', 'yell', 'yelp', 'yesterday', 'yield', 'yoke',
        'young', 'youth', 'yuan', 'yuck', 'yum', 'yup', 'yurt', 'zeal',
        'zero', 'zest', 'zig', 'zilch', 'zinc', 'zip', 'zone', 'zoo',
        'zoom', 'zucchini', 'zydeco', 'zygote', 'zymurgy',
    ]
    if w in y_glide_patterns:
        return ['y_glide']

    # vowel_uh: /ʌ/
    vowel_uh_patterns = [
        'cut', 'but', 'fun', 'run', 'cup', 'bus', 'nut', 'mud', 'hug',
        'duck', 'luck', 'stuck', 'gotta', 'hump', 'up', 'us', 'sun',
        'gun', 'bun', 'pup', 'pug', 'rug', 'bug', 'dug', 'tug', 'mug',
        'jug', 'cub', 'pub', 'sub', 'tub', 'rub', 'hub', 'bub', 'dub',
        'cud', 'bud', 'thud', 'stud', 'crud', 'drum', 'plum', 'slum',
        'strum', 'thumb', 'crumb', 'dumb', 'plumb', 'hull', 'bull',
        'full', 'pull', 'gull', 'cull', 'lull', 'null', 'skull', 'shrug',
        'chug', 'snug', 'thug',
    ]
    if w in vowel_uh_patterns:
        return ['vowel_uh']

    # vowel_ih: /ɪ/
    vowel_ih_patterns = [
        'hit', 'sit', 'big', 'lip', 'tip', 'fit', 'bit', 'dim', 'fin',
        'kin', 'pin', 'sin', 'win', 'thin', 'skin', 'slim', 'trim',
        'brim', 'clip', 'drip', 'flip', 'grip', 'sip', 'rip', 'zip',
        'dip', 'hip', 'nip', 'pip', 'rip', 'tip', 'vip', 'whip', 'chip',
        'ship', 'trip', 'strip', 'script', 'drift', 'gift', 'lift',
        'shift', 'sift', 'thrift', 'stiff', 'cliff', 'sniff', 'whiff',
        'skiff', 'bliss', 'kiss', 'miss', 'hiss', 'diss', 'fiss', 'wiss',
        'this', 'his', 'is', 'it', 'in', 'if', 'ill', 'bill', 'chill',
        'dill', 'fill', 'gill', 'hill', 'kill', 'mill', 'pill', 'rill',
        'till', 'will', 'zill', 'drill', 'frill', 'grill', 'skill',
        'spill', 'still', 'thrill', 'trill', 'brisk', 'disk', 'dusk',
        'frisk', 'husk', 'mask', 'risk', 'task', 'tusk', 'whisk', 'crisp',
    ]
    if w in vowel_ih_patterns:
        return ['vowel_ih']

    # vowel_ae: /æ/
    vowel_ae_patterns = [
        'cat', 'bat', 'hat', 'mat', 'flat', 'sat', 'rat', 'bad', 'mad',
        'sad', 'dad', 'lad', 'pad', 'fad', 'had', 'bag', 'tag', 'rag',
        'lag', 'nag', 'wag', 'zag', 'sag', 'gag', 'jag', 'mag', 'pug',
        'bug', 'dug', 'hug', 'jug', 'lug', 'mug', 'pug', 'rug', 'tug',
        'bug', 'chug', 'slugs', 'snug', 'thug', 'tugs', 'bugs', 'dugs',
        'hugs', 'jugs', 'mugs', 'pugs', 'rugs', 'tubs', 'cubs', 'pubs',
        'subs', 'buds', 'cuds', 'muds', 'thuds', 'studs', 'drums', 'plums',
        'slums', 'thumbs', 'crumbs', 'dumbs', 'hulls', 'bulls', 'fulls',
        'pulls', 'gulls', 'culls', 'lulls', 'nulls', 'skulls', 'shrugs',
        'chugs', 'snugs', 'thugs',
    ]
    if w in vowel_ae_patterns:
        return ['vowel_ae']

    # vowel_eh: /ɛ/
    vowel_eh_patterns = [
        'bed', 'red', 'led', 'fed', 'wed', 'shed', 'thread', 'bread',
        'dead', 'head', 'read', 'stead', 'tread', 'spread', 'dread',
        'shred', 'sled', 'bled', 'fled', 'pled', 'sped', 'shed', 'fed',
        'led', 'bed', 'red', 'wed', 'beg', 'leg', 'peg', 'keg', 'meg',
        'neg', 'seg', 'veg', 'wag', 'zag', 'sag', 'gag', 'jag', 'mag',
        'pug', 'bug', 'dug', 'hug', 'jug', 'lug', 'mug', 'pug', 'rug',
        'tug', 'bug', 'chug', 'slugs', 'snug', 'thug', 'tugs', 'bugs',
        'dugs', 'hugs', 'jugs', 'mugs', 'pugs', 'rugs', 'tubs', 'cubs',
        'pubs', 'subs', 'buds', 'cuds', 'muds', 'thuds', 'studs', 'drums',
        'plums', 'slums', 'thumbs', 'crumbs', 'dumbs', 'hulls', 'bulls',
        'fulls', 'pulls', 'gulls', 'culls', 'lulls', 'nulls', 'skulls',
        'shrugs', 'chugs', 'snugs', 'thugs',
    ]
    if w in vowel_eh_patterns:
        return ['vowel_eh']

    # vowel_ah: /ɑ/
    vowel_ah_patterns = [
        'hot', 'not', 'top', 'pot', 'lot', 'dot', 'box', 'fox', 'clock',
        'lock', 'rock', 'sock', 'mock', 'dock', 'flock', 'block', 'stock',
        'shock', 'knock', 'smock', 'trot', 'plot', 'slot', 'blot', 'clot',
        'grot', 'knot', 'snot', 'spot', 'swat', 'flat', 'brat', 'chat',
        'fat', 'gnat', 'mat', 'pat', 'rat', 'sat', 'vat', 'what', 'bat',
        'cat', 'hat', 'lat', 'nat', 'pat', 'rat', 'sat', 'vat', 'wat',
        'bot', 'cot', 'dot', 'got', 'hot', 'jot', 'lot', 'mot', 'not',
        'pot', 'rot', 'sot', 'tot', 'wot', 'zot',
    ]
    if w in vowel_ah_patterns:
        return ['vowel_ah']

    return []


# ---------------------------------------------------------------------------
# Load script and extract dialogue
# ---------------------------------------------------------------------------
def load_script(script_path: Path):
    with open(script_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def strip_stage_directions(text):
    """Remove stage directions in parentheses from dialogue text."""
    result = re.sub(r'\([^)]*\)', '', text).strip()
    # Normalize internal whitespace (collapse multiple spaces)
    result = re.sub(r'\s+', ' ', result)
    return result


def extract_dialogue_words(script_data):
    """Extract all dialogue lines with their context (prev/next lines)."""
    # First, collect all dialogue lines in order
    all_dialogues = []
    for line in script_data:
        if line.get('type') == 'dialogue':
            all_dialogues.append(line)

    dialogues = []
    for idx, line in enumerate(all_dialogues):
        text = line['text']
        # Strip stage directions for word extraction and storage
        spoken_text = strip_stage_directions(text)
        # Get prev and next dialogue lines for context (also stripped)
        prev_line = all_dialogues[idx - 1] if idx > 0 else None
        next_line = all_dialogues[idx + 1] if idx < len(all_dialogues) - 1 else None
        prev_spoken = strip_stage_directions(prev_line['text']) if prev_line else None
        next_spoken = strip_stage_directions(next_line['text']) if next_line else None

        # Extract individual words only from spoken dialogue
        words = re.findall(r'\b[a-zA-Z]+\b', spoken_text)
        for word in words:
            if len(word) <= 7:
                dialogues.append({
                    'word': word.lower(),
                    'full_line': spoken_text,
                    'character': line['character'],
                    'scene_id': line['scene_id'],
                    'line_index': line['line_index'],
                    'context_prev': f"{prev_line['character']}: {prev_spoken}" if prev_line and prev_spoken else None,
                    'context_next': f"{next_line['character']}: {next_spoken}" if next_line and next_spoken else None,
                })
    return dialogues


# ---------------------------------------------------------------------------
# Build cards from real transcript
# ---------------------------------------------------------------------------
def build_transcript_cards(dialogues):
    """Build cards from real transcript lines, grouped by pronunciation."""
    cards_by_focus = defaultdict(list)
    seen_words = set()

    for d in dialogues:
        word = d['word']
        if word in seen_words:
            continue
        seen_words.add(word)

        categories = classify_word(word)
        for focus in categories:
            cards_by_focus[focus].append({
                'target_word': word,
                'sentence_full': d['full_line'],
                'character': d['character'],
                'scene_id': d['scene_id'],
                'line_index': d['line_index'],
                'context_prev': d.get('context_prev'),
                'context_next': d.get('context_next'),
                'is_example_sentence': False,
            })

    return cards_by_focus


# ---------------------------------------------------------------------------
# Example sentences for supplementation
# ---------------------------------------------------------------------------
EXAMPLE_SENTENCES = {
    'vowel_uh': [
        ('cut', 'Be careful not to ___ yourself.', 'Be careful not to cut yourself.', '小心别切到自己。', 'cut 的过去式也是 cut。cut off=切断；cut out=剪掉。'),
        ('but', 'I want to, ___ I can\'t.', 'I want to, but I can\'t.', '我想去，但是我不能。', 'but 是最常用的转折连词。口语中常弱读为 /bət/。'),
        ('fun', 'That sounds like a lot of ___!', 'That sounds like a lot of fun!', '听起来很好玩！', 'fun 不可数名词：have fun=玩得开心。funny=好笑的（注意区别）。'),
        ('run', 'I ___ to work every morning.', 'I run to work every morning.', '我每天早上跑步去上班。', 'run-ran-run 不规则动词。run out of=用完；run into=偶遇。'),
        ('cup', 'Would you like a ___ of coffee?', 'Would you like a cup of coffee?', '你想来杯咖啡吗？', 'cup 一杯的量：a cup of tea。世界杯=the World Cup。'),
        ('bus', 'I take the ___ to school.', 'I take the bus to school.', '我坐公交车去学校。', 'bus 是可数名词。by bus=乘公交（不加 the）。school bus=校车。'),
        ('nut', 'I\'m allergic to ___ and peanuts.', 'I\'m allergic to nut and peanuts.', '我对坚果和花生过敏。', 'nut 坚果总称；peanut 花生；walnut 核桃。nut 也可指「疯子」。'),
        ('mud', 'The dog is covered in ___!', 'The dog is covered in mud!', '那只狗浑身都是泥！', 'mud 不可数名词。muddy=泥泞的。After the rain, the field was pure mud。'),
        ('hug', 'Come here and give me a ___!', 'Come here and give me a hug!', '过来给我一个拥抱！', 'hug 拥抱。give sb a hug=拥抱某人。hug 也可以指紧靠：the road hugs the coast。'),
        ('duck', 'Look at that ___ in the pond!', 'Look at that duck in the pond!', '看池塘里那只鸭子！', 'duck 鸭子；复数 ducks。动词 duck=迅速低头躲避。duck out=溜走。'),
    ],
    'vowel_ih': [
        ('hit', 'Don\'t ___ me!', 'Don\'t hit me!', '别打我！', 'hit-hit-hit 不规则动词。hit on sb=搭讪；hit it off=一拍即合。'),
        ('sit', 'Please have a seat and ___ down.', 'Please have a seat and sit down.', '请坐下。', 'sit-sat-sat。sit down=坐下；sit up=坐直；sit around=闲坐。'),
        ('big', 'That\'s a ___ house!', 'That\'s a big house!', '那是个大房子！', 'big 反义词=small/little。big deal=大事（常反讽）：Big deal! 那又怎样！'),
        ('lip', 'She bit her ___ nervously.', 'She bit her lip nervously.', '她紧张地咬了咬嘴唇。', 'lip 嘴唇。lips 复数。lipstick=口红。bite one\'s lip=咬唇（忍住不说）。'),
        ('tip', 'Leave a ___ for the waiter.', 'Leave a tip for the waiter.', '给服务员留点小费。', 'tip 小费；也指「建议/提示」：useful tips=实用小贴士。tip off=通风报信。'),
        ('fit', 'These shoes don\'t ___.', 'These shoes don\'t fit.', '这双鞋不合脚。', 'fit-fit-fit。fit in=融入；keep fit=保持健康。fit 也指「适合」：fit the purpose。'),
        ('bit', 'Just a ___, please.', 'Just a bit, please.', '只要一点点就好。', 'bit 是 bite 的过去式，也作名词「一点」：a bit of=一点儿。bit by bit=逐渐地。'),
        ('dim', 'The light is too ___ to read.', 'The light is too dim to read.', '灯光太暗了，没法看书。', 'dim 昏暗的；模糊的。dim memory=模糊的记忆。dim the lights=调暗灯光。'),
        ('fin', 'The shark has a huge ___ on its back.', 'The shark has a huge fin on its back.', '鲨鱼背上有个巨大的鳍。', 'fin 鱼鳍。shark fin=鱼翅。fin-to-tip=从鳍到尾（类似 nose-to-tail）。'),
        ('kin', 'She is ___ of mine.', 'She is kin of mine.', '她是我的亲戚。', 'kin 亲戚总称。next of kin=最近亲属。kindred=同族的。kind 种类←同源词。'),
    ],
    'vowel_ae': [
        ('cat', 'The ___ is sleeping on the sofa.', 'The cat is sleeping on the sofa.', '猫正在沙发上睡觉。', 'cat 猫。cat nap=打盹儿。let the cat out of the bag=泄露秘密。'),
        ('bat', 'He swung the ___ and hit the ball.', 'He swung the bat and hit the ball.', '他挥棒击中了球。', 'bat 两个意思：1.球棒（棒球）2.蝙蝠（动物）。at bat=轮击球。'),
        ('hat', 'Nice ___! Where did you get it?', 'Nice hat! Where did you get it?', '帽子不错！哪儿买的？', 'hat 帽子（有檐的）。cap=鸭舌帽。wear many hats=身兼多职。'),
        ('mat', 'Wipe your feet on the ___!', 'Wipe your feet on the mat!', '在垫子上擦擦脚！', 'mat 垫子。yoga mat=瑜伽垫。welcome mat=门口迎宾垫。'),
        ('flat', 'My ___ is just around the corner.', 'My flat is just around the corner.', '我的公寓就在拐角处。', 'flat 英式=公寓（美式=apartment）。also: 平的、扁平的。go flat=变平。'),
        ('sat', 'She ___ down and started reading.', 'She sat down and started reading.', '她坐下来开始看书。', 'sat 是 sit 的过去式/过去分词。sit-sat-sat。'),
        ('rat', 'There\'s a ___ in the basement!', 'There\'s a rat in the basement!', '地下室有只老鼠！', 'rat 老鼠（比 mouse 大）。smell a rat=觉察可疑。rat on sb=告发某人。'),
        ('bad', 'That\'s a really ___ idea.', 'That\'s a really bad idea.', '那是个很糟糕的主意。', 'bad-badly-badly（非正式）/bad-bad-worse-worst。bad news=坏消息。feel bad=感到抱歉。'),
        ('mad', 'Are you ___ at me?', 'Are you mad at me?', '你在生我的气吗？', 'mad 美式=生气的（=angry）；英式=疯狂的。go mad=发疯。mad at sb=生某人的气。'),
        ('sad', 'The movie ending was so ___.', 'The movie ending was so sad.', '电影结局太让人难过了。', 'sad-sadder-saddest。sadly=悲哀地。sad news=令人难过的消息。'),
    ],
    'vowel_eh': [
        ('bed', 'I\'m going to ___ early tonight.', 'I\'m going to bed early tonight.', '我今晚要早睡。', 'bed 床。go to bed=上床睡觉。in bed=在床上。bed room=卧室。'),
        ('red', 'She wore a ___ dress to the party.', 'She wore a red dress to the party.', '她穿了条红裙子去派对。', 'red 红色。see red=暴怒。red tape=繁文缛节。in the red=亏损。'),
        ('led', 'She ___ the team to victory.', 'She led the team to victory.', '她带领团队取得了胜利。', 'led 是 lead 的过去式。lead-led-led。led 也是 LED（发光二极管）的缩写。'),
        ('fed', 'He ___ the dog before leaving.', 'He fed the dog before leaving.', '他出门前喂了狗。', 'fed 是 feed 的过去式。feed-fed-fed。fed up=受够了。well-fed=吃得好的。'),
        ('wed', 'They ___ last spring.', 'They wed last spring.', '他们去年春天结婚了。', 'wed 结婚（正式/文学用词）。wedding=婚礼。wed-wed-wed。日常更常用 marry。'),
        ('shed', 'The tools are in the ___ out back.', 'The tools are in the shed out back.', '工具在后面那个棚屋里。', 'shed 两个意思：1.棚屋 2.脱落（shed tears/shed skin）。shed-shed-shed。'),
        ('thread', 'Can you pass me the needle and ___?', 'Can you pass me the needle and thread?', '能把针线递给我吗？', 'thread 线；线程（计算机）。lose the thread=跟不上思路。thread online=网络帖子。'),
        ('bread', 'I need to buy some ___ and milk.', 'I need to buy some bread and milk.', '我需要买些面包和牛奶。', 'bread 面包（不可数）。a loaf of bread=一条面包。bread and butter=生计。'),
        ('dead', 'The battery is completely ___.', 'The battery is completely dead.', '电池完全没电了。', 'dead 死的；没电的。dead tired=累死了（夸张）。in dead silence=鸦雀无声。'),
        ('head', 'Use your ___ sometimes!', 'Use your head sometimes!', '你偶尔也用用脑子吧！', 'head 头；头脑。head of=…的负责人。head over heels=完全地（常用于爱情）。'),
    ],
    'vowel_ah': [
        ('hot', 'It\'s really ___ outside today.', 'It\'s really hot outside today.', '今天外面真的很热。', 'hot 热的。hot dog=热狗。hot water=热水。get hot=变热。'),
        ('not', 'I\'m ___ sure about that.', 'I\'m not sure about that.', '我对此不太确定。', 'not 否定词。not at all=一点也不。if not=如果不。not necessarily=未必。'),
        ('top', 'Put the book on ___ of the shelf.', 'Put the book on top of the shelf.', '把书放在架子顶上。', 'top 顶部。on top of=在…上面。top it off=最后加上。from top to bottom=从头到尾。'),
        ('pot', 'The ___ is boiling on the stove.', 'The pot is boiling on the stove.', '锅在炉子上烧开了。', 'pot 锅、壶。flower pot=花盆。pot of gold=一罐金子。potluck=自带菜聚餐。'),
        ('lot', 'Thanks a ___ for your help!', 'Thanks a lot for your help!', '非常感谢你的帮助！', 'lot 许多。a lot of=很多。parking lot=停车场。lot 也指「地块」。'),
        ('dot', 'Sign on the ___ please.', 'Sign on the dot please.', '请在点处签名。', 'dot 点。on the dot=准时。dot the i\'s=给 i 加点（做事仔细）。connect the dots=连点成图。'),
        ('box', 'What\'s in the ___?', 'What\'s in the box?', '盒子里是什么？', 'box 盒子。box office=票房。think outside the box=跳出思维定式。'),
        ('fox', 'The ___ is very clever.', 'The fox is very clever.', '狐狸非常狡猾。', 'fox 狐狸。sly as a fox=像狐狸一样狡猾。Fox 也是福克斯新闻频道。'),
        ('clock', 'The ___ says it\'s three o\'clock.', 'The clock says it\'s three o\'clock.', '钟显示三点了。', 'clock 时钟。o\'clock=…点钟。clock in/out=打卡。around the clock=全天候。'),
        ('lock', 'Don\'t forget to ___ the door.', 'Don\'t forget to lock the door.', '别忘了锁门。', 'lock 锁。lock up=锁好。under lock and key=锁起来。lock screen=锁屏。'),
    ],
    'r_colored': [
        ('her', 'I gave ___ a present.', 'I gave her a present.', '我送了她一份礼物。', 'her 她的/她（宾格）。发音 /h/ 是典型卷舌元音。'),
        ('bird', 'A ___ landed on the windowsill.', 'A bird landed on the windowsill.', '一只鸟落在了窗台上。', 'bird 鸟。early bird=早起的人。bird brain=笨蛋。birds of a feather=一丘之貉。'),
        ('work', 'I have a lot of ___ to do.', 'I have a lot of work to do.', '我有很多工作要做。', 'work 工作。work out=锻炼/解决。work on=从事。out of work=失业。'),
        ('turn', 'It\'s your ___ to go.', 'It\'s your turn to go.', '轮到你了。', 'turn 转动；轮到。take turns=轮流。turn on/off=开/关。turn out=结果是。'),
        ('girl', 'The ___ next door is my friend.', 'The girl next door is my friend.', '隔壁那个女孩是我朋友。', 'girl 女孩。girlfriend=女朋友/闺蜜。girls\' night=闺蜜之夜。'),
        ('word', 'I don\'t know what this ___ means.', 'I don\'t know what this word means.', '我不知道这个词什么意思。', 'word 单词。in a word=简言之。have a word with=和…说两句。keep one\'s word=守信。'),
        ('nurse', 'The ___ checked my blood pressure.', 'The nurse checked my blood pressure.', '护士量了我的血压。', 'nurse 护士。nurse 也作动词：nurse a baby=喂奶。nurse back to health=护理康复。'),
        ('church', 'We go to ___ every Sunday.', 'We go to church every Sunday.', '我们每个星期天去教堂。', 'church 教堂。go to church=做礼拜。church mouse=一贫如洗（as poor as a church mouse）。'),
        ('burn', 'Don\'t ___ the toast!', 'Don\'t burn the toast!', '别把吐司烤焦了！', 'burn-burnt/burned-burnt/burned。burn out=烧尽/筋疲力尽。burn calories=消耗热量。'),
        ('shirt', 'This ___ is too tight.', 'This shirt is too tight.', '这件衬衫太紧了。', 'shirt 衬衫。T-shirt=T 恤。keep your shirt on=别激动。shirt off your back=倾其所有。'),
    ],
    'o_diphthong': [
        ('go', 'Let\'s ___ to the park.', 'Let\'s go to the park.', '我们去公园吧。', 'go-go-went-gone。go on=继续；go off=爆炸/响铃；go out=出去玩。'),
        ('no', '___, I don\'t think so.', 'No, I don\'t think so.', '不，我不这么认为。', 'no 否定回答。no problem=没问题；no way=没门/不会吧；no wonder=难怪。'),
        ('so', '___ what happened next?', 'So what happened next?', '那后来呢？', 'so 所以/那么。so that=以便；so so=一般般；so far=到目前为止。'),
        ('show', 'Can you ___ me how to do it?', 'Can you show me how to do it?', '你能给我演示怎么做吗？', 'show-showed-shown。show off=炫耀；show up=出现。TV show=电视节目。'),
        ('know', 'I don\'t ___ what to say.', 'I don\'t know what to say.', '我不知道该说什么。', 'know-knew-known。know about=了解；get to know=逐渐认识。You know=你知道的（口头禅）。'),
        ('grow', 'Kids ___ so fast!', 'Kids grow so fast!', '孩子们长得太快了！', 'grow-grew-grown。grow up=长大；grow into=成长为。grow out of=长大不再做。'),
        ('throw', 'Don\'t ___ things at me!', 'Don\'t throw things at me!', '别朝我扔东西！', 'throw-threw-thrown。throw away=扔掉；throw up=呕吐。throw a party=办派对。'),
        ('blow', 'The wind ___ really hard.', 'The wind blows really hard.', '风刮得很大。', 'blow-blew-blown。blow out=吹灭；blow up=爆炸/放大。blow it=搞砸了（口语）。'),
        ('slow', 'You\'re driving too ___!', 'You\'re driving too slow!', '你开得太慢了！', 'slow 慢的。slow down=慢下来。slow and steady=稳扎稳打。slow motion=慢动作。'),
        ('snow', 'It\'s going to ___ tomorrow.', 'It\'s going to snow tomorrow.', '明天要下雪了。', 'snow 雪。snowflake=雪花。snowball=雪球。snowed in=被大雪困住。'),
    ],
    'long_e': [
        ('see', 'I can ___ the ocean from here.', 'I can see the ocean from here.', '我从这里能看到大海。', 'see-saw-seen。see off=送行；see through=看穿。let\'s see=让我想想。'),
        ('me', 'Can you help ___?', 'Can you help me?', '你能帮帮我吗？', 'me 是 I 的宾格。excuse me=打扰一下；help me=帮我。'),
        ('tree', 'There\'s a big ___ in the yard.', 'There\'s a big tree in the yard.', '院子里有棵大树。', 'tree 树。family tree=家谱。decision tree=决策树。tree house=树屋。'),
        ('free', 'Is this seat ___?', 'Is this seat free?', '这个座位有人吗？', 'free 免费的；自由的。for free=免费地。free of charge=免费。feel free=请随意。'),
        ('three', 'I need ___ more minutes.', 'I need three more minutes.', '我还需要三分钟。', 'three 三。three-dimensional=三维的。three cheers=三呼万岁。'),
        ('key', 'I lost my ___ again!', 'I lost my key again!', '我又把钥匙弄丢了！', 'key 钥匙；关键。key point=关键点。low-key=低调。key in=输入（键盘）。'),
        ('need', 'I ___ a cup of coffee right now.', 'I need a cup of coffee right now.', '我现在需要一杯咖啡。', 'need 需要。in need of=需要。require=更正式的同义词。require=需要（正式）。'),
        ('keep', '___ going! Don\'t stop!', 'Keep going! Don\'t stop!', '继续！别停！', 'keep-kept-kept。keep on=继续；keep up=保持。keep in touch=保持联系。'),
        ('feel', 'I ___ really tired today.', 'I feel really tired today.', '我今天觉得很累。', 'feel-felt-felt。feel like=想要/感觉像。feel free to=请随意。feel bad=感到抱歉。'),
        ('week', 'See you next ___!', 'See you next week!', '下周见！', 'week 周。weekday=工作日；weekend=周末。this week=这周。week by week=逐周。'),
    ],
    'schwa': [
        ('sofa', 'Sit on the ___ and relax.', 'Sit on the sofa and relax.', '坐沙发上休息吧。', 'sofa 沙发。末尾的 /ə/ 是典型 schwa。couch 是同义词。'),
        ('panda', 'The ___ is eating bamboo.', 'The panda is eating bamboo.', '熊猫正在吃竹子。', 'panda 熊猫。末尾 /ə/ 是 schwa。panda eyes=熊猫眼（熬夜后的黑眼圈）。'),
        ('about', 'What\'s this ___?', 'What\'s this about?', '这是关于什么的？', 'about 关于。how about=…怎么样？about to=即将。talk about=谈论。'),
        ('alone', 'She lives ___.', 'She lives alone.', '她独自生活。', 'alone 独自的。all alone=完全独自。leave alone=不打扰。let alone=更不用说。'),
        ('banana', 'I ate a ___ for breakfast.', 'I ate a banana for breakfast.', '我早餐吃了根香蕉。', 'banana 香蕉。三个 /ə/ schwa 音！go bananas=发狂/激动。banana split=香蕉船。'),
        ('doctor', 'I need to see a ___.', 'I need to see a doctor.', '我需要看医生。', 'doctor 医生。末尾 /ɚ/ 是 r-colored schwa。PhD = Doctor of Philosophy。'),
        ('actor', 'He wants to be an ___.', 'He wants to be an actor.', '他想当演员。', 'actor 演员（男/通用）。actress=女演员。末尾 /ɚ/ 是 r-colored schwa。'),
        ('problem', 'No ___! I can help.', 'No problem! I can help.', '没问题！我来帮忙。', 'problem 问题。no problem=没问题。math problem=数学题。末尾 /əm/ 含 schwa。'),
        ('today', 'What day is ___?', 'What day is today?', '今天星期几？', 'today 今天。首音节 /tə/ 是 schwa。today 口语常快读为 /təˈdeɪ/。'),
        ('support', 'I ___ you all the way!', 'I support you all the way!', '我全力支持你！', 'support 支持。首音节 /sə/ 是 schwa。support group=互助小组。in support of=支持。'),
    ],
    'flap_t': [
        ('better', 'You can do ___!', 'You can do better!', '你可以做得更好！', 'better 更好的。better 中 t 发闪音 /ɾ/。better off=更好；better yet=更好的是。'),
        ('water', 'Can I have a glass of ___?', 'Can I have a glass of water?', '能给我一杯水吗？', 'water 水。t 发闪音 /ɾ/。water bottle=水瓶。water down=稀释。'),
        ('little', 'Just a ___ bit more!', 'Just a little bit more!', '再多一点点！', 'little 小的。a little=一点；little by little=逐渐。t 发闪音。'),
        ('butter', 'Pass me the ___, please.', 'Pass me the butter, please.', '请把黄油递给我。', 'butter 黄油。t 发闪音 //。butter up=拍马屁。bread and butter=生计。'),
        ('pretty', 'That\'s a ___ dress!', 'That\'s a pretty dress!', '那条裙子真漂亮！', 'pretty 漂亮的；相当。pretty 中 t 发闪音。pretty much=差不多。'),
        ('ladder', 'I need a ___ to reach the roof.', 'I need a ladder to reach the roof.', '我需要一架梯子才能够到屋顶。', 'ladder 梯子。t 发闪音 /ɾ/。climb the ladder=往上爬（比喻晋升）。'),
        ('letter', 'I got a ___ from my friend.', 'I got a letter from my friend.', '我收到了朋友的来信。', 'letter 信；字母。t 发闪音 /ɾ/。pen pal=笔友。cover letter=求职信。'),
        ('kitty', 'The ___ is playing with yarn.', 'The kitty is playing with yarn.', '小猫在玩毛线。', 'kitty 小猫（口语/儿语）。t 发闪音。也指「赌注池/共同资金」：the kitty。'),
        ('matter', 'It doesn\'t ___ to me.', 'It doesn\'t matter to me.', '对我来说无所谓。', 'matter 要紧；事情。t 发闪音。What\'s the matter?=怎么了？no matter=无论。'),
        ('bottle', 'Pass me that ___ of wine.', 'Pass me that bottle of wine.', '把那瓶酒递给我。', 'bottle 瓶子。t 发闪音 /ɾ/。bottle up=压抑（情感）。bottle opener=开瓶器。'),
    ],
    'weak_forms': [
        ('to', 'I went ___ the store.', 'I went to the store.', '我去了商店。', 'to 强读 /tuː/，弱读 /tə/。口语中几乎总是弱读。to do=去做；to be or not to be。'),
        ('for', 'This is ___ you.', 'This is for you.', '这是给你的。', 'for 强读 /fɔr/，弱读 /fɚ/。for sure=确定；for now=暂时。'),
        ('and', 'Bread ___ butter.', 'Bread and butter.', '面包和黄油。', 'and 强读 /ænd/，弱读 /ənd/ 或 /ən/。and so on=等等。rock and roll。'),
        ('of', 'A cup ___ tea, please.', 'A cup of tea, please.', '请来杯茶。', 'of 强读 /ɑv/，弱读 /əv/。of course=当然。a lot of=很多。'),
        ('can', '___ you help me?', 'Can you help me?', '你能帮我吗？', 'can 强读 /kæn/，弱读 /kən/。can\'t 不能。can do=能做到。'),
        ('was', 'He ___ very happy.', 'He was very happy.', '他当时很开心。', 'was 强读 /wɑz/，弱读 /wəz/。was 是 am/is 的过去式。'),
        ('some', 'Would you like ___ coffee?', 'Would you like some coffee?', '你想来点咖啡吗？', 'some 一些。some 强读 /sʌm/，弱读 /səm/。somebody=某人；something=某物。'),
        ('that', 'I think ___ it\'s true.', 'I think that it\'s true.', '我认为那是真的。', 'that 强读 /ðæt/，弱读 /ðət/。口语中 that 常弱读甚至省略。'),
        ('from', 'I\'m ___ China.', 'I\'m from China.', '我来自中国。', 'from 强读 /frɑm/，弱读 /frəm/。from now on=从现在起。far from=远非。'),
        ('have', 'I ___ got an idea!', 'I have got an idea!', '我有个主意！', 'have 强读 /hæv/，弱读 /həv/。have to=必须。have got=有（口语）。'),
    ],
    'y_glide': [
        ('you', '___ look great today!', 'You look great today!', '你今天看起来很棒！', 'you 你/你们。起始 /j/ 是 y 滑音。you know=你知道的（口头禅）。'),
        ('yes', '___, I agree with you.', 'Yes, I agree with you.', '是的，我同意你。', 'yes 是的。起始 /j/ 是 y 滑音。yes or no=是还是不是。'),
        ('yet', 'I haven\'t finished ___.', 'I haven\'t finished yet.', '我还没做完。', 'yet 还/尚未。起始 /j/ 滑音。not yet=还没。yet again=又一次。'),
        ('use', 'Can I ___ your phone?', 'Can I use your phone?', '我能用一下你的手机吗？', 'use 使用。起始 /j/ 滑音。use up=用完。make use of=利用。'),
        ('cute', 'That puppy is so ___!', 'That puppy is so cute!', '那只小狗太可爱了！', 'cute 可爱的。/kjuːt/ 中 /j/ 是 y 滑音。cute 也指聪明的。'),
        ('few', 'Only a ___ people showed up.', 'Only a few people showed up.', '只有几个人来了。', 'few 少的。a few=一些；few=几乎没有。few and far between=稀少。'),
        ('new', 'I got a ___ job!', 'I got a new job!', '我找到新工作了！', 'new 新的。/nju/ 含 /j/ 滑音。brand new=全新。new to=对…来说是新。'),
        ('view', 'The ___ from here is amazing!', 'The view from here is amazing!', '这里的景色太美了！', 'view 景色；观点。/vjuː/ 含 /j/ 滑音。in view of=鉴于。on view=展出。'),
        ('music', 'I love listening to ___!', 'I love listening to music!', '我喜欢听音乐！', 'music 音乐。/mjuː/ 含 /j/ 滑音。play music=播放音乐。music festival=音乐节。'),
        ('unite', 'We must ___ to win.', 'We must unite to win.', '我们必须团结才能赢。', 'unite 团结。/ju/ 起始含 /j/ 滑音。united=团结的。United States=美国。'),
    ],
}


# ---------------------------------------------------------------------------
# IPA and POS lookup
# ---------------------------------------------------------------------------
WORD_IPA = {
    'cut': '/kʌt/', 'but': '/bʌt/', 'fun': '/fʌn/', 'run': '/rʌn/', 'cup': '/kʌp/',
    'bus': '/bʌs/', 'nut': '/nʌt/', 'mud': '/mʌd/', 'hug': '/hʌɡ/', 'duck': '/dʌk/',
    'hit': '/hɪt/', 'sit': '/sɪt/', 'big': '/bɪɡ/', 'lip': '/lɪp/', 'tip': '/tɪp/',
    'fit': '/fɪt/', 'bit': '/bɪt/', 'dim': '/dɪm/', 'fin': '/fɪn/', 'kin': '/kɪn/',
    'cat': '/kæt/', 'bat': '/bæt/', 'hat': '/hæt/', 'mat': '/mæt/', 'flat': '/flæt/',
    'sat': '/sæt/', 'rat': '/ræt/', 'bad': '/bæd/', 'mad': '/mæd/', 'sad': '/sæd/',
    'bed': '/bɛd/', 'red': '/rɛd/', 'led': '/lɛd/', 'fed': '/fɛd/', 'wed': '/wɛd/',
    'shed': '/ɛd/', 'thread': '/θrɛd/', 'bread': '/brɛd/', 'dead': '/dɛd/', 'head': '/hɛd/',
    'hot': '/hɑt/', 'not': '/nɑt/', 'top': '/tɑp/', 'pot': '/pɑt/', 'lot': '/lɑt/',
    'dot': '/dɑt/', 'box': '/bɑks/', 'fox': '/fɑks/', 'clock': '/klɑk/', 'lock': '/lɑk/',
    'her': '/hɝ/', 'bird': '/bɝd/', 'work': '/wɝk/', 'turn': '/tn/', 'girl': '/ɡɝl/',
    'word': '/wɝd/', 'nurse': '/nɝs/', 'church': '/tʃɝtʃ/', 'burn': '/bɝn/', 'shirt': '/ʃɝt/',
    'go': '/ɡoʊ/', 'no': '/noʊ/', 'so': '/soʊ/', 'show': '/ʃoʊ/', 'know': '/noʊ/',
    'grow': '/ɡroʊ/', 'throw': '/θroʊ/', 'blow': '/bloʊ/', 'slow': '/sloʊ/', 'snow': '/snoʊ/',
    'see': '/siː/', 'me': '/miː/', 'tree': '/triː/', 'free': '/friː/', 'three': '/θriː/',
    'key': '/kiː/', 'need': '/niːd/', 'keep': '/kiːp/', 'feel': '/fiːl/', 'week': '/wiːk/',
    'sofa': '/ˈsoʊfə/', 'panda': '/ˈpændə/', 'about': '/əˈbaʊt/', 'alone': '/əˈloʊn/',
    'banana': '/bəˈnænə/', 'doctor': '/ˈdɑktɚ/', 'actor': '/ˈæktɚ/', 'problem': '/ˈprɑbləm/',
    'today': '/təˈdeɪ/', 'support': '/səˈpɔrt/',
    'better': '/ˈbɛɾɚ/', 'water': '/ˈwɔɾɚ/', 'little': '/ˈlɪɾəl/', 'butter': '/bʌɾɚ/',
    'pretty': '/ˈprɪɾi/', 'ladder': '/ˈlæɚ/', 'letter': '/ˈlɾɚ/', 'kitty': '/ˈkɪɾi/',
    'matter': '/ˈmæɾɚ/', 'bottle': '/ˈbɑɾəl/',
    'to': '/tə/', 'for': '/fɚ/', 'and': '/ənd/', 'of': '/əv/', 'can': '/kən/',
    'was': '/wəz/', 'some': '/səm/', 'that': '/ðət/', 'from': '/frəm/', 'have': '/həv/',
    'you': '/juː/', 'yes': '/jɛs/', 'yet': '/jɛt/', 'use': '/juːz/', 'cute': '/kjuːt/',
    'few': '/fjuː/', 'new': '/nuː/', 'view': '/vjuː/', 'music': '/ˈmjuːzɪk/', 'unite': '/juˈnaɪt/',
}

WORD_POS = {
    'cut': 'v. 切；割', 'but': 'conj. 但是', 'fun': 'n. 乐趣', 'run': 'v. 跑', 'cup': 'n. 杯子',
    'bus': 'n. 公共汽车', 'nut': 'n. 坚果', 'mud': 'n. 泥巴', 'hug': 'v./n. 拥抱', 'duck': 'n. 鸭子',
    'hit': 'v. 打；击中', 'sit': 'v. 坐', 'big': 'adj. 大的', 'lip': 'n. 嘴唇', 'tip': 'n. 小费',
    'fit': 'v./adj. 适合', 'bit': 'n. 一点', 'dim': 'adj. 昏暗的', 'fin': 'n. 鱼鳍', 'kin': 'n. 亲戚',
    'cat': 'n. 猫', 'bat': 'n. 球棒；蝙蝠', 'hat': 'n. 帽子', 'mat': 'n. 垫子', 'flat': 'adj. 平的',
    'sat': 'v. 坐了', 'rat': 'n. 老鼠', 'bad': 'adj. 坏的', 'mad': 'adj. 生气的', 'sad': 'adj. 伤心的',
    'bed': 'n. 床', 'red': 'adj. 红色的', 'led': 'v. 带领', 'fed': 'v. 喂养', 'wed': 'v. 结婚',
    'shed': 'n. 棚屋', 'thread': 'n. 线', 'bread': 'n. 面包', 'dead': 'adj. 死的', 'head': 'n. 头',
    'hot': 'adj. 热的', 'not': 'adv. 不', 'top': 'n. 顶部', 'pot': 'n. 锅', 'lot': 'n. 许多',
    'dot': 'n. 点', 'box': 'n. 盒子', 'fox': 'n. 狐狸', 'clock': 'n. 钟', 'lock': 'v./n. 锁',
    'her': 'pron. 她的', 'bird': 'n. 鸟', 'work': 'v./n. 工作', 'turn': 'v./n. 转', 'girl': 'n. 女孩',
    'word': 'n. 单词', 'nurse': 'n. 护士', 'church': 'n. 教堂', 'burn': 'v. 燃烧', 'shirt': 'n. 衬衫',
    'go': 'v. 去', 'no': 'adv. 不', 'so': 'adv. 所以', 'show': 'v./n. 展示', 'know': 'v. 知道',
    'grow': 'v. 成长', 'throw': 'v. 扔', 'blow': 'v. 吹', 'slow': 'adj. 慢的', 'snow': 'n. 雪',
    'see': 'v. 看见', 'me': 'pron. 我', 'tree': 'n. 树', 'free': 'adj. 免费的', 'three': 'num. 三',
    'key': 'n. 钥匙', 'need': 'v. 需要', 'keep': 'v. 保持', 'feel': 'v. 感觉', 'week': 'n. 周',
    'sofa': 'n. 沙发', 'panda': 'n. 熊猫', 'about': 'prep. 关于', 'alone': 'adj. 独自',
    'banana': 'n. 香蕉', 'doctor': 'n. 医生', 'actor': 'n. 演员', 'problem': 'n. 问题',
    'today': 'adv./n. 今天', 'support': 'v./n. 支持',
    'better': 'adj. 更好的', 'water': 'n. 水', 'little': 'adj. 小的', 'butter': 'n. 黄油',
    'pretty': 'adj. 漂亮的', 'ladder': 'n. 梯子', 'letter': 'n. 信', 'kitty': 'n. 小猫',
    'matter': 'v./n. 要紧', 'bottle': 'n. 瓶子',
    'to': 'prep. 到', 'for': 'prep. 为了', 'and': 'conj. 和', 'of': 'prep. …的', 'can': 'v. 能',
    'was': 'v. 是', 'some': 'adj. 一些', 'that': 'conj. 那个', 'from': 'prep. 从', 'have': 'v. 有',
    'you': 'pron. 你', 'yes': 'adv. 是的', 'yet': 'adv. 还', 'use': 'v. 使用', 'cute': 'adj. 可爱的',
    'few': 'adj. 少的', 'new': 'adj. 新的', 'view': 'n. 景色', 'music': 'n. 音乐', 'unite': 'v. 团结',
}

WORD_LEVEL = {
    'cut': 'A1', 'but': 'A1', 'fun': 'A1', 'run': 'A1', 'cup': 'A1', 'bus': 'A1', 'nut': 'A2',
    'mud': 'A2', 'hug': 'A2', 'duck': 'A1', 'hit': 'A1', 'sit': 'A1', 'big': 'A1', 'lip': 'A2',
    'tip': 'A2', 'fit': 'A2', 'bit': 'A2', 'dim': 'B1', 'fin': 'B1', 'kin': 'B2',
    'cat': 'A1', 'bat': 'A2', 'hat': 'A1', 'mat': 'A2', 'flat': 'A2', 'sat': 'A1', 'rat': 'A2',
    'bad': 'A1', 'mad': 'A2', 'sad': 'A1', 'bed': 'A1', 'red': 'A1', 'led': 'A2', 'fed': 'A2',
    'wed': 'B1', 'shed': 'B1', 'thread': 'B1', 'bread': 'A1', 'dead': 'A1', 'head': 'A1',
    'hot': 'A1', 'not': 'A1', 'top': 'A1', 'pot': 'A2', 'lot': 'A1', 'dot': 'A2', 'box': 'A1',
    'fox': 'A2', 'clock': 'A1', 'lock': 'A2', 'her': 'A1', 'bird': 'A1', 'work': 'A1', 'turn': 'A1',
    'girl': 'A1', 'word': 'A1', 'nurse': 'A2', 'church': 'A2', 'burn': 'A2', 'shirt': 'A1',
    'go': 'A1', 'no': 'A1', 'so': 'A1', 'show': 'A1', 'know': 'A1', 'grow': 'A2', 'throw': 'A2',
    'blow': 'A2', 'slow': 'A1', 'snow': 'A1', 'see': 'A1', 'me': 'A1', 'tree': 'A1', 'free': 'A1',
    'three': 'A1', 'key': 'A1', 'need': 'A1', 'keep': 'A1', 'feel': 'A1', 'week': 'A1',
    'sofa': 'A1', 'panda': 'A2', 'about': 'A1', 'alone': 'A2', 'banana': 'A1', 'doctor': 'A1',
    'actor': 'A2', 'problem': 'A1', 'today': 'A1', 'support': 'A2',
    'better': 'A1', 'water': 'A1', 'little': 'A1', 'butter': 'A2', 'pretty': 'A1', 'ladder': 'B1',
    'letter': 'A1', 'kitty': 'A2', 'matter': 'A1', 'bottle': 'A1',
    'to': 'A1', 'for': 'A1', 'and': 'A1', 'of': 'A1', 'can': 'A1', 'was': 'A1', 'some': 'A1',
    'that': 'A1', 'from': 'A1', 'have': 'A1', 'you': 'A1', 'yes': 'A1', 'yet': 'A2', 'use': 'A1',
    'cute': 'A1', 'few': 'A2', 'new': 'A1', 'view': 'A2', 'music': 'A1', 'unite': 'B1',
}

# Chinese translations for target words (used in preview & flashcard front)
WORD_TRANSLATION = {
    'a': '一（个）', 'about': '关于；大约', 'actor': '演员', 'alone': '独自的',
    'and': '和', 'be': '是', 'bed': '床', 'better': '更好的', 'big': '大的',
    'boat': '船', 'cup': '杯子', 'cut': '切；割', 'dad': '爸爸', 'dead': '死的',
    'does': '做（do的第三人称）', 'done': '完成', 'down': '向下', 'feel': '感觉',
    'first': '第一', 'fun': '乐趣', 'go': '去', 'gonna': '将要（going to）',
    'got': '得到（get的过去式）', 'gotta': '必须（got to）', 'happy': '开心的',
    'hat': '帽子', 'have': '有', 'he': '他', 'head': '头', 'her': '她的',
    'his': '他的', 'how': '怎样', 'hump': '驼峰', 'it': '它', 'keep': '保持',
    'kill': '杀', 'know': '知道', 'leg': '腿', 'little': '小的', 'lot': '许多',
    'luck': '运气', 'me': '我', 'need': '需要', 'new': '新的', 'no': '不',
    'not': '不', 'now': '现在', 'phone': '电话', 'pot': '锅', 'pretty': '漂亮的',
    'really': '真的', 'red': '红色的', 'rub': '摩擦', 'see': '看见', 'she': '她',
    'shock': '震惊', 'sip': '小口喝', 'sit': '坐', 'so': '所以', 'some': '一些',
    'spot': '地点；斑点', 'still': '仍然', 'strip': '脱掉；条纹', 'sweet': '甜的',
    'the': '（定冠词）', 'this': '这个', 'tip': '小费；提示', 'to': '到',
    'today': '今天', 'turn': '转', 'up': '向上', 'us': '我们', 'very': '非常',
    'waiting': '等待', 'wanna': '想要（want to）', 'we': '我们', 'week': '周',
    'what': '什么', 'will': '将', 'with': '和…一起', 'word': '单词',
    'work': '工作', 'world': '世界', 'worm': '虫子', 'yes': '是的', 'you': '你',
}

# Full sentence translations (idiomatic Chinese for Friends S01E01 dialogue)
SENTENCE_TRANSLATIONS = {
    "All right Joey, be nice.  So does he have a hump?* A hump and a hairpiece?":
        "行了Joey，别损人了。所以他到底有没有驼背？* 一个驼背还戴假发？",
    "So you wanna tell us now, or are we waiting for four wet bridesmaids?":
        "你是打算现在告诉我们呢，还是等着四个哭花妆的伴娘一起说？",
    "Hi, come in! Paul, this is.. (They are all lined up next to the door.)... everybody, everybody, this is Paul.":
        "嗨，进来！Paul，这是……（大家排成一排站在门口）……大家，这是Paul。",
    "Here's a little tip, she really likes it when you rub her neck in the same spot over and over and over again until it starts to get a little red.":
        "给你个小秘诀，她就喜欢你在她脖子同一个地方反复揉，揉到微微发红。",
    "Yes, please don't spoil all this fun.":
        "是啊，别扫了大家的兴。",
    "Oh, look, wish me luck!":
        "哦，祝我好运吧！",
    "C'mon, cut. Cut, cut, cut,...":
        "来吧，剪！剪剪剪……",
    "Yeah. Yeah, I'll have a cup of coffee.":
        "好啊，给我来杯咖啡。",
    "Okay, everybody relax. This is not even a date.* It's just two people going out to dinner and- not having sex.":
        "好了大家别紧张，这根本不算约会。* 就是两个人出去吃个饭，然后——不发生关系。",
    "This guy says hello, I wanna* kill myself.":
        "那男的跟我打了个招呼，我想*死的心都有了。",
    "Strip joint! C'mon, you're single! Have some hormones!":
        "脱衣舞俱乐部！拜托，你现在单身！释放一下荷尔蒙嘛！",
    "And I just want a million dollars! (He extends his hand hopefully.)":
        "而我只想要一百万美金！（满怀希望地伸出手）",
    "Oh God Monica hi! Thank God! I just went to your building and you weren't there and then this guy with a big hammer said you might be here and you are, you are!":
        "天哪Monica！谢天谢地！我刚去你公寓你不在，然后一个拿大锤的哥们说你可能在这儿，你真的在，你真的在！",
    "If I let go of my hair, my head will fall off.":
        "我要是松开头发，脑袋就要掉下来了。",
    "Change!  Okay, sit down. (Shows Paul in) Two seconds.":
        "换话题！好了，坐下。（把Paul带进来）两秒钟就好。",
    "Stay out of my freezer! [Scene: A Restaurant, Monica and Paul are still eating.]":
        "别碰我冰箱里的东西！",
    "Well, ever-ev-... ever since she left me, um, I haven't been able to, uh, perform. (Monica takes a sip of her drink.) ...Sexually.":
        "嗯，自……自从她离开我之后，我就……嗯，没法……（Monica喝了口饮料）…… perform 了。",
    "I told mom and dad last night, they seemed to take* it pretty well.":
        "我昨晚告诉爸妈了，他们好像还挺能接受的。",
    "Okay, look, this is probably for the best, y'know? Independence. Taking control of your life.  The whole, 'hat' thing.*":
        "好吧，这样也许是最好的，你知道？独立，掌控自己的人生。就是那个'帽子'的事。*",
    "-leg?":
        "——腿？",
    "You should both know, that he's a dead man.  Oh, Chandler? (Starts after Chandler.)":
        "你们俩都给我记住，他死定了。哦，Chandler？（追Chandler）",
    "I assume we're looking for an answer more sophisticated than 'to get you into bed'.":
        "我猜你想要的答案应该比'为了把你骗上床'更有深度吧。",
    'Oh really, so that hysterical phone call I got from a woman at sobbing 3:00 A.M., "I\'ll never have grandchildren, I\'ll never have grandchildren." What':
        "哦是吗，那凌晨三点我接到一个女人哭天抢地的电话，'我永远抱不上孙子了'，这又是怎么回事？",
    "Alright Ross, look. You're feeling a lot of pain right now. You're angry. You're hurting*":
        "好了Ross，听着。你现在很痛苦，你很愤怒，你在受伤*",
    "(spitting out her drink in shock) Oh God, oh God, I am sorry... I am so sorry...":
        "（震惊地喷出口中的饮料）天哪，天哪，对不起……我太对不起你了……",
    "Listen, while you're on a roll, if you feel like you gotta make like a Western omelet or something... (Joey and Chandler taste the coffee, grimace, and pour it into a plant pot.) Although actually I'm really not that hungry...":
        "听着，既然你都做了，要不顺便做个西式蛋饼什么的……（Joey和Chandler尝了口咖啡，一脸嫌弃地倒进花盆）虽然其实我也不是很饿……",
    "There's nothing to tell! He's just some guy I work with!":
        "没什么好说的！他就是我一个同事！",
    "Just, 'cause, I don't want her to go* through what I went through with Carl- oh!":
        "只是，因为，我不想让她*经历我跟Carl那段破事——哦！",
    "(sings) Raindrops on roses and rabbits and kittens, (Rachel and Monica turn to look at her.) bluebells*":
        "（唱）玫瑰上的雨滴，还有小兔子和小猫咪，（Rachel和Monica转头看她）风铃草*",
    "(squatting and reading the instructions) I'm supposed to attach a brackety thing to the side things, using a bunch of these little worm guys. I have no brackety thing, I see no whim guys whatsoever and- I cannot feel my legs.":
        "（蹲着看说明书）我应该把一个'支架玩意儿'装到'边边玩意儿'上，用一堆'小螺丝玩意儿'。可我既没有'支架玩意儿'，也看不到什么'螺丝玩意儿'，而且——我的腿没知觉了。",
    "Give her a break, it's hard being on your own for the first time.":
        "放过她吧，第一次独立生活不容易。",
    "The word you're looking for is 'Anyway'...":
        "你想说的词应该是'总之'……",
    "Welcome to the real world! It sucks. You're gonna love it!":
        "欢迎来到现实世界！它烂透了。但你会爱上它的！",
    "Then I look down, and I realize there's a phone... there.":
        "然后我低头一看，发现那儿有个电话……在那儿。",
    "No.":
        "不。",
    "All of a sudden, the phone starts to ring. Now I don't know what to do, everybody starts looking at me.":
        "突然电话响了，我不知所措，所有人都盯着我看。",
    "No!! Okay?! Why does everyone keep fixating* on that? She didn't know, how should I know?":
        "没有！！行了吧？！为什么所有人都揪着*这个不放？她都不知道，我怎么会知道？",
    "Oh God... well, it started about a half hour before the wedding. I was in the room where we were keeping all the presents, and I was looking at this gravy boat. This really gorgeous Lamauge gravy boat":
        "天哪……嗯，大概婚礼前半小时吧，我在放礼物的房间，看着一个酱汁船。一个特别漂亮的Limoges酱汁船",
    "Done with the bookcase!":
        "书架搞定了！",
    "Sounds* like a date to me.":
        "听起来*就是约会嘛。",
    "I just feel like someone reached down my throat, grabbed* my small intestine,":
        "我就感觉有人把手伸进我喉咙，抓住了*我的小肠，",
    "Ooh! Oh! (She starts to pluck* at the air just in front of Ross.)":
        "哦！哦！（她开始在Ross面前*拨弄空气）",
    "You can see where he'd have trouble.":
        "你能看出他哪儿有问题了。",
    "Well, maybe that's my decision. Well, maybe I don't need your money. Wait!! Wait, I said maybe!!":
        "嗯，也许那是我自己的决定。嗯，也许我不需要你的钱。等等！！等等，我说的是也许！！",
    "I know, I know, I'm such an idiot. I guess I should have caught on when she started going to the dentist four and five times a week. I mean, how clean can teeth get?":
        "我知道，我知道，我就是个白痴。我早该在她一周去看四五次牙医的时候就察觉到的。我是说，牙还能有多干净？",
    "(explaining to the others) Carol moved* her stuff out today.":
        "（跟其他人解释）Carol今天把*她的东西搬走了。",
    "No, no don't! Stop cleansing my aura! No, just leave my aura alone, okay?":
        "不不不！别净化我的气场！不，就让我气场待着别管，好吗？",
    "(singing) Love is sweet as summer showers, love is a wondrous work of art, but your love oh your love, your love...is like a giant pigeon...crapping on my heart.  La-la-la-la-la- (some guy gives her some change and to that guy) Thank you. (sings":
        "（唱）爱情如夏雨般甜蜜，爱情是奇妙的艺术品，但你的爱啊你的爱，你的爱……就像一只巨大的鸽子……在我心上拉屎。啦啦啦啦啦——（有人给了她零钱，对那人说）谢谢。（继续唱",
    "Yeah, I'm an actor.":
        "是啊，我是个演员。",
    "C'mon,* you're going out with the guy! There's gotta*":
        "拜托，*你都要跟那男的约会了！肯定*",
    "Finally, I figure* I'd better answer it, and it turns out it's my mother, which is very-very weird,":
        "最后我想*还是接一下吧，结果是我妈打来的，这就非常非常奇怪了，",
    "I'll be fine, alright? Really, everyone. I hope she'll be very happy.":
        "我会没事的，好吗？真的，大家。我希望她能幸福。",
    "Well actually thanks, but I think I'm just gonna hang out here tonight.  It's been kinda a long day.":
        "嗯，谢谢，不过我想今晚就待在这儿了。今天挺累的。",
    "Yes!":
        "是的！",
    "They're my new 'I don't need a job, I don't need my parents, I've got great boots' boots!":
        "这是我的新'我不需要工作，不需要爸妈，我有超棒的靴子'靴子！",
    "Shut up, Joey!":
        "闭嘴，Joey！",
    "Change! Okay, sit down. Two seconds.":
        "换话题！好了，坐下。两秒钟就好。",
    "Are you kidding? I take credit for Paul. Y'know before me, there was no snap in his turtle for two years.":
        "开什么玩笑？Paul能重振雄风全靠我。你知道在我之前，他可有两年都不行。",
    "Oh, you wouldn't know a great butt if it came up and bit ya.":
        "你要是有个好屁股你也认不出来，就算它跳起来咬你一口。",
    "You should both know, that he's a dead man. Oh, Chandler?":
        "你们俩都给我记住，他死定了。哦，Chandler？",
    "I'm supposed to attach a brackety thing to the side things, using a bunch of these little worm guys. I have no brackety thing, I see no whim guys whatsoever and- I cannot feel my legs.":
        "（蹲着看说明书）我应该把一个'支架玩意儿'装到'边边玩意儿'上，用一堆'小螺丝玩意儿'。可我既没有'支架玩意儿'，也看不到什么'螺丝玩意儿'，而且——我的腿没知觉了。",
    "Carol moved* her stuff out today.":
        "Carol今天把*她的东西搬走了。",
    "Love is sweet as summer showers, love is a wondrous work of art, but your love oh your love, your love...is like a giant pigeon...crapping on my heart. La-la-la-la-la- Thank you. (sings":
        "（唱）爱情如夏雨般甜蜜，爱情是奇妙的艺术品，但你的爱啊你的爱，你的爱……就像一只巨大的鸽子……在我心上拉屎。啦啦啦啦啦——谢谢。（继续唱",
}

# Context line translations (prev/next dialogue)
CONTEXT_TRANSLATIONS = {
    "Joey: C'mon,* you're going out with the guy! There's gotta*": "Joey：拜托，*你都要跟那男的约会了！肯定*",
    "Phoebe: Wait, does he eat chalk?*": "Phoebe：等等，他吃粉笔吗？*",
    "Ross: Hi.": "Ross：嗨。",
    "Phoebe: What does that mean? Does he sell it, drink it, or just complain a lot?": "Phoebe：那是什么意思？他是卖酒、喝酒，还是光抱怨？",
    "All: Hey! Paul! Hi! The Wine Guy! Hey!": "大家：嘿！Paul！嗨！那个卖酒的！嘿！",
    "Paul: Yeah?": "Paul：是吗？",
    "Monica: Shut up, Joey!": "Monica：（从卧室喊）闭嘴，Joey！",
    "Joey: Hey-hey-hey-hey, if you're gonna start with that stuff* we're outta": "Joey：喂喂喂，你要是又开始那套*我们就走了",
    "Joey: Ross, let me ask you a question. She got the furniture, the stereo, the good TV- what did you get?": "Joey：Ross，我问你个问题。她拿了家具、音响、好电视——你拿到了什么？",
    "Monica: What for?": "Monica：干嘛？",
    "All: Cut, cut, cut, cut, cut, cut, cut...": "大家：剪！剪剪剪剪剪……（她剪了一张，大家欢呼）",
    "Rachel: I'm just serving it.": "Rachel：我只是端过来而已。",
    "Chandler: Kids, new dream... I'm in Las Vegas.": "Chandler：各位，新梦……我在拉斯维加斯。（Rachel坐下来听Chandler的梦）",
    "Chandler: Sounds* like a date to me.": "Chandler：听起来*就是约会嘛。",
    "Ross: Hi.": "Ross：（尴尬得要死）嗨。",
    "Monica: Are you okay, sweetie?*": "Monica：你还好吗，亲爱的？*",
    "Joey: Alright Ross, look. You're feeling a lot of pain right now. You're angry. You're hurting*": "Joey：好了Ross，听着。你现在很痛苦，你很愤怒，你在受伤*",
    "Ross: I don't want to be single, okay? I just... I just- I just wanna be married again!": "Ross：我不想单身，好吗？我只是……我只是——我只是想再结一次婚！",
    "Monica: Rachel?!": "Monica：Rachel？！",
    "Chandler: Sometimes I wish I was a lesbian... Did I say that out loud?": "Chandler：有时候我希望自己是个拉拉……（大家都盯着他）我说出声了？",
    "Joey: And you never knew she was a lesbian...": "Joey：而你一直不知道她是个拉拉……",
    "Chandler: Cookie?": "Chandler：饼干？",
    "Phoebe: Ooh! Oh!": "Phoebe：哦！哦！（她开始在Ross面前*拨弄空气）",
    "Phoebe: Fine! Be murky!": "Phoebe：好吧！就让你气场浑浊着！",
    "Monica: Who wasn't invited to the wedding.": "Monica：谁没被邀请参加婚礼。",
    "Phoebe: Oh, I wish I could, but I don't want to.": "Phoebe：哦，我希望我能，但我不想。",
    "Monica: Yeah, we all have jobs. See, that's how we buy stuff.": "Monica：是啊，我们都有工作。你看，我们就是这么买东西的。",
    "Rachel: Wow! Would I have seen you in anything?": "Rachel：哇！我在什么剧里见过你吗？",
    "Monica: And they weren't looking at you before?!": "Monica：那他们之前没在看你？！",
    "Ross: He finally asked you out?": "Ross：他终于约你了？",
    "Chandler: Ooh, this is a Dear Diary moment.": "Chandler：哦，这是'亲爱的日记'时刻。",
    "Chandler: Yes, and we're very excited about it.": "Chandler：（面无表情）是的，我们非常激动。",
    "Ross: Okay, sure.": "Ross：好的，当然。",
    "Chandler: Oh, how well you know me...": "Chandler：哦，你太了解我了……",
    "Monica: How'd you pay for them?": "Monica：你怎么付的钱？",
    "All: Oh, yeah. Had that dream.": "大家：哦，对，做过那个梦。",
    "Chandler: I have no idea.": "Chandler：我完全不知道。",
    "Joey: Never had that dream.": "Joey：没做过那个梦。",
    "Phoebe: I helped!": "Phoebe：（笑着走到厨房对Chandler和Joey说）我帮忙了！",
    "Phoebe: No.": "Phoebe：不。",
    "Ross: A wandering?": "Ross：流浪？",
    "Ross: Sorry.": "Ross：抱歉。",
    "Ross: Thanks.": "Ross：谢谢。",
    "Chandler: All finished!": "Chandler：全搞定了！",
    "Joey: I'm thinking we've got a bookcase here.": "Joey：我觉得我们这儿有个书架。",
    "Joey: Instead of...?": "Joey：而不是……？",
    "Monica: Oh good, Lenny and Squigy are here.": "Monica：（进来，自言自语）哦好，Lenny和Squigy来了。",
    "Monica: All right, you ready?": "Monica：好了，准备好了吗？",
    "Monica: I hate men! I hate men!": "Monica：我恨男人！我恨男人！",
    "Monica: No you don't.": "Monica：你不会的。",
    "Monica: Well, that's it You gonna crash* on the couch?": "Monica：好吧，就这样（对Ross）你要在沙发上*凑合睡吗？",
    "Paul: That's one way! Me, I- I went for the watch.": "Paul：（笑）这也是一种方法！我嘛，我——我选了手表。",
    "Paul: Ever since she walked out on me, I, uh...": "Paul：自从她离开我之后，我，呃……",
    "Paul: It's okay...": "Paul：没事的……",
    "Phoebe: Ooh, I just pulled out four eyelashes. That can't be good.": "Phoebe：哦，我刚拔了四根睫毛。这不太好。",
    "Rachel: I'm all better now.": "Rachel：我现在好多了。",
    "Rachel: Thank you.": "Rachel：谢谢。",
    "Waitress: Can I get you some coffee?": "服务员：要给你们来点咖啡吗？",
    # Additional context translations for lines not in original dict
    "Monica: So how you doing today? Did you sleep okay? Talk to Barry? I can't stop smiling.": "Monica：今天怎么样？睡得好吗？跟Barry谈了？我笑得停不下来。",
    "Ross: There's an image.": "Ross：那画面太美。",
    "Monica: My brother's going through that right now, he's such a mess. How did you get through it?": "Monica：我哥现在就在经历这个，他一团糟。你是怎么走出来的？",
    "Joey: Strip joint! C'mon, you're single! Have some hormones!": "Joey：脱衣舞俱乐部！拜托，你单身！释放一下荷尔蒙嘛！",
    "Chandler: Ooh, she should not be wearing those pants.*": "Chandler：哦，她不该穿那条裤子。*",
    "Chandler: Alright, so I'm back in high school, I'm standing in the middle of the cafeteria,*": "Chandler：好吧，我回到高中，站在自助餐厅中间，*",
    "Ross: So Rachel, what're you, uh... what're you up to tonight?": "Ross：所以Rachel，你，呃……今晚有什么安排？",
    "Monica: I hate men! I hate men!": "Monica：我恨男人！我恨男人！",
    "Ross: I'm supposed to attach a brackety thing to the side things, using a bunch of these little worm guys. I have no brackety thing, I see no whim guys whatsoever and- I cannot feel my legs.": "Ross：（蹲着看说明书）我应该把一个'支架玩意儿'装到'边边玩意儿'上……我的腿没知觉了。",
    "Rachel: Look Daddy, it's my life. Well maybe I'll just stay here with Monica.": "Rachel：爸爸，这是我的人生。好吧也许我就跟Monica住这儿了。",
    "Monica: Okay, everybody relax. This is not even a date.* It's just two people going out to dinner and- not having sex.": "Monica：好了大家别紧张，这根本不算约会。* 就是两个人出去吃个饭，然后——不发生关系。",
    "Rachel: Oh God... well, it started about a half hour before the wedding. I was in the room where we were keeping all the presents, and I was looking at this gravy boat. This really gorgeous Lamauge gravy boat": "Rachel：天哪……嗯，大概婚礼前半小时，我在放礼物的房间，看着一个特别漂亮的Limoges酱汁船",
    "Joey: And hey, you need anything, you can always come to Joey. Me and Chandler live across the hall. And he's away a lot.": "Joey：嘿，你需要什么随时来找Joey。我和Chandler住对门。而且他经常不在。",
    "Monica: Just breathe, breathe.. that's it. Just try to think of nice calm things...": "Monica：深呼吸，深呼吸……就这样。试着想些美好平静的事……",
    "Monica: Well, that's it You gonna crash* on the couch?": "Monica：好吧，就这样（对Ross）你要在沙发上*凑合睡吗？",
    "Chandler: All of a sudden, the phone starts to ring. Now I don't know what to do, everybody starts looking at me.": "Chandler：突然电话响了，我不知所措，所有人都盯着我看。",
    "Joey: Ohh.": "Joey：哦。",
    "Chandler: Sometimes I wish I was a lesbian... Did I say that out loud?": "Chandler：有时候我希望自己是个拉拉……（大家都盯着他）我说出声了？",
    "Joey: Of course it was a line!": "Joey：那当然是搭讪的话！",
    "Monica: I said that you had a nice butt, it's just not a great butt.": "Monica：我说你屁股不错，只是不算特别棒。",
    "Monica: You mean you know Paul like I know Paul?": "Monica：你是说你了解Paul就像我了解Paul那样？",
    "Monica: Why?! Why? Why, why would anybody do something like that?": "Monica：为什么？！为什么？为什么有人要这么做？",
    "Rachel: C'mon Daddy, listen to me! It's like, it's like, all of my life, everyone has always told me, 'You're a shoe! You're a shoe, you're a shoe, you're a shoe!'. And today I just stopped and I said, 'What if I don't wanna be a sho": "Rachel：拜托爸爸，听我说！就好像，就好像，我这一辈子，所有人都跟我说，'你是一只鞋！'然后今天我突然停下来想，'如果我不想当一只鞋呢？'",
    "Phoebe: Love is sweet as summer showers, love is a wondrous work of art, but your love oh your love, your love...is like a giant pigeon...crapping on my heart. La-la-la-la-la- Thank you. (sings": "Phoebe：（唱）爱情如夏雨般甜蜜……就像一只巨大的鸽子在我心上拉屎。啦啦啦——谢谢。",
    "Monica: I think we are getting a little ahead of selves here. Okay. Okay. I am just going to get up, go to work and not think about him all day. Or else I'm just gonna get up and go to work.": "Monica：我觉得我们有点想太多了。好吧。我就起床、上班、一整天不想他。不然我就起床去上班。",
    "Joey: Here's a little tip, she really likes it when you rub her neck in the same spot over and over and over again until it starts to get a little red.": "Joey：给你个小秘诀，她就喜欢你在她脖子同一个地方反复揉，揉到微微发红。",
    "Ross: I told mom and dad last night, they seemed to take* it pretty well.": "Ross：我昨晚告诉爸妈了，他们好像还挺能接受的。",
    "Paul: Well, you might try accidentally breaking something valuable of hers, say her-": "Paul：嗯，你可以试试'不小心'打碎她什么贵重东西，比如她的——",
    "Phoebe: You're welcome. I remember wh": "Phoebe：不客气。我记得……",
    "Monica: Oh my God!": "Monica：我的天！",
    "Ross: I honestly don't know if I'm hungry or horny.": "Ross：我真的不知道我是饿了还是欲火焚身。",
    "Chandler: Y'know, if you listen closely, you can hear a thousand retailers scream.": "Chandler：你知道吗，仔细听，你能听到一千家商店在尖叫。",
    "Rachel: Daddy, I just... I can't marry him! I'm sorry. I just don't love him. Well, it matters to me!": "Rachel：（打电话）爸爸，我只是……我嫁不了他！对不起。我就是不爱他。嗯，这对我很重要！",
    "Monica: Well, I guess we've established who's staying here with Monica...": "Monica：好吧，看来我们已经确定谁要跟Monica住了……",
    "Phoebe: Fine! Be murky!": "Phoebe：好吧！就让你气场浑浊着！",
    "Monica: There's nothing to tell! He's just some guy I work with!": "Monica：没什么好说的！他就是我一个同事！",
    "Ross: Come on, you made coffee! You can do anything!": "Ross：拜托，你都能煮咖啡了！你什么都能做到！",
    "Rachel: I know that. That's why I was getting married.": "Rachel：我知道。所以我才要结婚啊。",
    "Phoebe: Just, 'cause, I don't want her to go* through what I went through with Carl- oh!": "Phoebe：只是，因为，我不想让她*经历我跟Carl那段破事——哦！",
    "Chandler: You're right, I'm sorry. 'Once I was a wooden boy, a little wooden boy...'": "Chandler：你说得对，对不起。'曾经我是一个木头男孩，一个小木头男孩……'",
    "Chandler: You're right, I'm sorry. \"Once I was a wooden boy, a little wooden boy...\"": "Chandler：你说得对，对不起。'曾经我是一个木头男孩，一个小木头男孩……'",
    "Monica: So you wanna tell us now, or are we waiting for four wet bridesmaids?": "Monica：你是打算现在告诉我们呢，还是等着四个哭花妆的伴娘一起说？",
    "Chandler: All right Joey, be nice. So does he have a hump?* A hump and a hairpiece?": "Chandler：行了Joey，别损人了。所以他到底有没有驼背？* 一个驼背还戴假发？",
    "Monica: Oh really, so that hysterical phone call I got from a woman at sobbing 3:00 A.M., \"I'll never have grandchildren, I'll never have grandchildren.\" What": "Monica：哦是吗，那凌晨三点我接到一个女人哭天抢地的电话，'我永远抱不上孙子了'，这又是怎么回事？",
}


def lookup_context_translation(text):
    """Look up context translation with fuzzy matching (normalized whitespace)."""
    if not text:
        return ''
    # Direct match
    if text in CONTEXT_TRANSLATIONS:
        return CONTEXT_TRANSLATIONS[text]
    # Fuzzy match: normalize whitespace and try again
    normalized = re.sub(r'\s+', ' ', text).strip()
    for key, value in CONTEXT_TRANSLATIONS.items():
        if re.sub(r'\s+', ' ', key).strip() == normalized:
            return value
    return ''


def lookup_sentence_translation(text):
    """Look up sentence translation with fuzzy matching."""
    if not text:
        return ''
    if text in SENTENCE_TRANSLATIONS:
        return SENTENCE_TRANSLATIONS[text]
    normalized = re.sub(r'\s+', ' ', text).strip()
    for key, value in SENTENCE_TRANSLATIONS.items():
        if re.sub(r'\s+', ' ', key).strip() == normalized:
            return value
    return ''

# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------
def main():
    root = Path(__file__).resolve().parent.parent
    script_path = root / 'src' / 'data' / 'S01E01_script.json'
    src_data_dir = root / 'src' / 'data'
    out_dir = root / 'public' / 'episodes' / 'S01E01'
    src_data_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load script
    script_data = load_script(script_path)
    dialogues = extract_dialogue_words(script_data)

    # Build transcript cards
    transcript_cards = build_transcript_cards(dialogues)

    # Supplement with examples where needed
    all_cards = []
    counter = 1

    for focus in ['vowel_uh', 'vowel_ih', 'vowel_ae', 'vowel_eh', 'vowel_ah',
                  'r_colored', 'o_diphthong', 'long_e', 'schwa', 'flap_t',
                  'weak_forms', 'y_glide']:
        focus_transcript = transcript_cards.get(focus, [])
        focus_examples = EXAMPLE_SENTENCES.get(focus, [])

        # Add transcript cards first
        for card_data in focus_transcript[:10]:
            word = card_data['target_word']
            all_cards.append({
                'id': f'S01E01_{counter:03d}',
                'episode': 'S01E01',
                'scene_id': card_data['scene_id'],
                'line_index': card_data['line_index'],
                'character': card_data['character'],
                'target_word': word,
                'ipa': WORD_IPA.get(word, '/.../'),
                'pos': WORD_POS.get(word, 'n.'),
                'level': WORD_LEVEL.get(word, 'B1'),
                'pronunciation_focus': focus,
                'tags': ['台词'],
                'sentence_cloze': card_data['sentence_full'].replace(word, '___', 1),
                'sentence_full': card_data['sentence_full'],
                'translation': WORD_TRANSLATION.get(word, ''),
                'sentence_translation': SENTENCE_TRANSLATIONS.get(card_data['sentence_full'], '') or lookup_sentence_translation(card_data['sentence_full']),
                'cultural_note': f'来自 S01E01 台词，{card_data["character"]} 所说。',
                'context_prev': card_data.get('context_prev'),
                'context_prev_cn': lookup_context_translation(card_data.get('context_prev', '')),
                'context_next': card_data.get('context_next'),
                'context_next_cn': lookup_context_translation(card_data.get('context_next', '')),
                'screenshot': '/episodes/S01E01/images/scene_001_central_perk.png',
                'frequency_rank': None,
                'is_example_sentence': False,
            })
            counter += 1

        # Supplement with examples if needed
        needed = 10 - len(focus_transcript[:10])
        if needed > 0:
            for example in focus_examples[:needed]:
                word, cloze, full, trans, note = example
                all_cards.append({
                    'id': f'S01E01_{counter:03d}',
                    'episode': 'S01E01',
                    'scene_id': 'scene_001_central_perk',
                    'line_index': 0,
                    'character': 'Example',
                    'target_word': word,
                    'ipa': WORD_IPA.get(word, '/.../'),
                    'pos': WORD_POS.get(word, 'n.'),
                    'level': WORD_LEVEL.get(word, 'B1'),
                    'pronunciation_focus': focus,
                    'tags': ['示例句'],
                    'sentence_cloze': cloze,
                    'sentence_full': full,
                    'translation': trans,
                    'sentence_translation': trans,
                    'cultural_note': note,
                    'context_prev': None,
                    'context_prev_cn': None,
                    'context_next': None,
                    'context_next_cn': None,
                    'screenshot': '/episodes/S01E01/images/scene_001_central_perk.png',
                    'frequency_rank': None,
                    'is_example_sentence': True,
                })
                counter += 1

    # Write output
    cards_json = json.dumps(all_cards, ensure_ascii=False, indent=2)
    (src_data_dir / 'S01E01_cards.json').write_text(cards_json, encoding='utf-8')
    (out_dir / 'cards.json').write_text(cards_json, encoding='utf-8')

    print(f'[OK] Generated {len(all_cards)} flashcards')
    print(f'  -> {src_data_dir / "S01E01_cards.json"}')
    print(f'  -> {out_dir / "cards.json"}')

    # Validation
    from collections import Counter
    focus_counts = Counter(c['pronunciation_focus'] for c in all_cards)
    print('\n=== Validation ===')
    for focus, count in sorted(focus_counts.items()):
        status = 'OK' if count >= 10 else 'FAIL'
        print(f'  [{status}] {focus}: {count} cards')

    long_words = [c for c in all_cards if len(c['target_word'].replace(' ', '')) > 7]
    if long_words:
        print(f'  [FAIL] Words > 7 letters:')
        for c in long_words:
            print(f'    - \'{c["target_word"]}\' ({len(c["target_word"].replace(" ", ""))} letters)')
    else:
        print(f'  [OK] All words <= 7 letters')

    transcript_count = sum(1 for c in all_cards if not c.get('is_example_sentence'))
    example_count = sum(1 for c in all_cards if c.get('is_example_sentence'))
    print(f'  [INFO] Transcript cards: {transcript_count}')
    print(f'  [INFO] Example cards: {example_count}')

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
