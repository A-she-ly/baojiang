"""
Script: parse_s01e01.py
Purpose:
  1. Strip RTF formatting from the Friends S01E01 transcript.
  2. Parse scenes, character lines, and footnotes.
  3. Build structured JSON files: metadata.json, script.json, cards.json (hand-picked phrases).

Run:
  python baojiang-english/scripts/parse_s01e01.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# RTF stripper (lightweight — works for this specific document)
# ---------------------------------------------------------------------------
def strip_rtf(text: str) -> str:
    """Remove RTF control words, groups, and return plain text with \n line endings."""
    # Remove {\* ... } destination groups first (non-rendered)
    text = re.sub(r"\{\\\*[^}]*\}", "", text)

    out: List[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "{":
            depth += 1
            i += 1
            continue
        if c == "}":
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0:
            out.append(c)
            i += 1
            continue
        # Inside group:
        if c == "\\":
            # Control word (optional parameter then delimiter)
            m = re.match(r"\\([a-zA-Z]+)(-?\d+)? ?", text[i:])
            if m:
                word = m.group(1)
                # \par = paragraph break -> newline; \line = line break
                if word in ("par", "line"):
                    out.append("\n")
                i += len(m.group(0))
                continue
            # Escaped character: \\, \{, \}, \~, \-, etc.
            if i + 1 < n:
                ch = text[i + 1]
                if ch in ("\\", "{", "}"):
                    out.append(ch)
                    i += 2
                    continue
                if ch == "'":
                    # 2-hex-byte
                    hex_str = text[i + 2 : i + 4]
                    try:
                        out.append(bytes.fromhex(hex_str).decode("cp1252", errors="replace"))
                    except Exception:
                        pass
                    i += 4
                    continue
            i += 1
            continue
        # Regular char inside group: append if it's real text
        out.append(c)
        i += 1

    plain = "".join(out)
    # Collapse blank lines
    plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
    return plain


# ---------------------------------------------------------------------------
# Transcript parser
# ---------------------------------------------------------------------------
SCENE_RE = re.compile(r"^\[Scene:\s*(.+?)\]?$", re.IGNORECASE)
TIME_LAPSE_RE = re.compile(r"^\[(Time Lapse|Commercial Break|Cut to[^\]]*)\]", re.IGNORECASE)
ACTION_RE = re.compile(r"^\([^)]+\)$")
CHAR_LINE_RE = re.compile(r"^([A-Z][A-Za-z\s\-']+?):\s*(.+)$")
# Sometimes names end with a parenthetical stage direction: Rachel (on phone): ...
CHAR_LINE_DIR_RE = re.compile(r"^([A-Z][A-Za-z\s\-']+?)\s*(\([^)]+\))?:\s*(.+)$")


def parse_script(plain: str) -> Dict[str, Any]:
    lines = [ln.rstrip() for ln in plain.splitlines()]

    # Collect metadata header (before first [Scene:])
    header: List[str] = []
    body_start = 0
    for idx, ln in enumerate(lines):
        if SCENE_RE.match(ln.strip()):
            body_start = idx
            break
        header.append(ln)
    header_text = "\n".join(header).strip()

    # Extract title from header
    title = "The One Where Monica Gets a New Roommate"
    m = re.search(r"(The One Where[^-\n]+)", header_text)
    if m:
        title = m.group(1).strip()

    scenes: List[Dict[str, Any]] = []
    current_scene: Dict[str, Any] | None = None
    scene_counter = 0

    def new_scene(name: str) -> Dict[str, Any]:
        nonlocal scene_counter
        scene_counter += 1
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        return {
            "scene_id": f"scene_{scene_counter:03d}_{slug}",
            "scene_name": name,
            "lines": [],
        }

    line_index = 0
    characters = set()

    for ln in lines[body_start:]:
        s = ln.strip()
        if not s:
            continue

        # New scene
        m_scene = SCENE_RE.match(s)
        if m_scene:
            name = m_scene.group(1).rstrip(".").strip()
            current_scene = new_scene(name)
            scenes.append(current_scene)
            continue

        # Time lapse / commercial break — treat as scene note
        if TIME_LAPSE_RE.match(s):
            if current_scene is None:
                current_scene = new_scene("Opening")
                scenes.append(current_scene)
            current_scene["lines"].append({
                "line_index": line_index,
                "type": "note",
                "text": s,
            })
            line_index += 1
            continue

        # Action in parentheses: "(They all stare, bemused.)"
        if ACTION_RE.match(s):
            if current_scene is None:
                current_scene = new_scene("Opening")
                scenes.append(current_scene)
            current_scene["lines"].append({
                "line_index": line_index,
                "type": "action",
                "text": s[1:-1].strip(),
            })
            line_index += 1
            continue

        # Character line (with optional parenthetical direction)
        m_cl = CHAR_LINE_DIR_RE.match(s)
        if m_cl:
            character = m_cl.group(1).strip()
            direction = (m_cl.group(2) or "").strip()
            if direction:
                direction = direction[1:-1].strip()
            speech = m_cl.group(3).strip()
            if current_scene is None:
                current_scene = new_scene("Opening")
                scenes.append(current_scene)
            characters.add(character)
            current_scene["lines"].append({
                "line_index": line_index,
                "type": "dialogue",
                "character": character,
                "direction": direction or None,
                "text": speech,
            })
            line_index += 1
            continue

        # Anything else: treat as note
        if current_scene is None:
            current_scene = new_scene("Opening")
            scenes.append(current_scene)
        current_scene["lines"].append({
            "line_index": line_index,
            "type": "note",
            "text": s,
        })
        line_index += 1

    metadata = {
        "episode": "S01E01",
        "title": title,
        "title_cn": "莫妮卡的新室友",
        "description": "The pilot episode — Rachel leaves her fiancé at the altar and moves in with Monica; Ross is devastated after his wife Carol leaves him for a woman.",
        "scenes_count": len(scenes),
        "dialogue_lines_count": line_index,
        "characters": sorted(characters),
        "scenes_summary": [
            {"scene_id": s["scene_id"], "scene_name": s["scene_name"], "lines_count": len(s["lines"])}
            for s in scenes
        ],
    }
    return {"metadata": metadata, "scenes": scenes}


# ---------------------------------------------------------------------------
# Hand-picked flashcards for S01E01
# Curated: phrasal verbs, idioms, colloquialisms, CET4-6 words, useful patterns
# ---------------------------------------------------------------------------
def build_cards(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Helper: find first line_index in a scene where a target substring appears in dialogue
    def find_line(scene_name_keyword: str, substr: str) -> tuple[str, int, str, str]:
        for s in scenes:
            if scene_name_keyword.lower() in s["scene_name"].lower():
                for ln in s["lines"]:
                    if ln["type"] == "dialogue" and substr.lower() in ln["text"].lower():
                        return s["scene_id"], ln["line_index"], ln["character"], ln["text"]
        # Fallback: search all scenes
        for s in scenes:
            for ln in s["lines"]:
                if ln["type"] == "dialogue" and substr.lower() in ln["text"].lower():
                    return s["scene_id"], ln["line_index"], ln["character"], ln["text"]
        return scenes[0]["scene_id"], 0, "Chandler", "…"

    # IPA values use General American (GenAm); each focus selects one primary listening target.
    cards_raw = [
        # ---- Opening / Central Perk ----
        ("gotta", "/ˈɡɑɾə/", "contraction (got to)", "B1", "flap_t", ["contraction", "连读", "口语缩写"],
         "There's ___ be something wrong with him!",
         "There's gotta be something wrong with him!",
         "他肯定有什么毛病！",
         "gotta = got to 的口语连读，同类还有 gonna=going to、wanna=want to、hafta=have to。",
         "Central Perk", "gotta"),

        ("hump", "/hʌmp/", "n. 驼背；隆起", "C1", "vowel_uh", ["身体词汇", "幽默"],
         "So does he have a ___? A hump and a hairpiece?",
         "So does he have a hump? A hump and a hairpiece?",
         "他难道是个驼子？驼背上还戴着假发？",
         "hump 本义驼峰/驼背；hairpiece 假发。Chandler 在夸张调侃 Monica 的约会对象。",
         "Central Perk", "hump"),

        ("drifted apart", "/ˈdrɪftɪd əˈpɑrt/", "phrasal verb 渐行渐远", "B2", "vowel_ih", ["phrasal_verb", "关系"],
         "You and I have kinda ___.",
         "You and I have kinda drifted apart.",
         "我们俩这些年有点疏远了。",
         "drift apart = 关系慢慢变淡；kinda = kind of。",
         "Central Perk", "drifted apart"),

        ("turned on by", "/tɝnd ɑn baɪ/", "phrase 被…吸引；对…有性趣", "B2", "r_colored", ["俚语", "phrasal"],
         "I was more ___ this gravy boat than by Barry!",
         "I was more turned on by this gravy boat than by Barry!",
         "我居然对这个肉汁船（餐具）比对Barry更有感觉！",
         "turn sb on = 使某人兴奋/有性趣（日常也可指对某事物很有热情）。Rachel 神比喻。",
         "Monica's Apartment", "turned on by"),

        ("gravy boat", "/ˈɡreɪvi boʊt/", "n. 船形调味汁碟", "B2", "o_diphthong", ["生活词汇", "餐具"],
         "I was looking at this gorgeous Lamauge ___.",
         "I was looking at this gorgeous Lamauge gravy boat.",
         "我盯着那只漂亮的拉莫奇肉汁船看。",
         "gravy 肉汁/酱汁；boat 船形器皿。西方餐桌上用来盛gravy的小船形碟子。",
         "Monica's Apartment", "gravy boat"),

        ("freaked out", "/frikt aʊt/", "phrasal verb 崩溃；吓尿", "B1", "long_e", ["phrasal_verb", "情绪"],
         "And then I got really ___.",
         "And then I got really freaked out.",
         "然后我就彻底慌了神。",
         "freak out 口语高频：受惊、激动、情绪失控。也可说 sb freaks me out（某人吓着我了）。",
         "Monica's Apartment", "freaked out"),

        ("hit on her", "/hɪɾ ɑn hɚ/", "phrase 搭讪；撩", "B2", "flap_t", ["俚语", "phrasal", "约会"],
         "Joey, stop ___ her!",
         "Joey, stop hitting on her!",
         "Joey你别撩她了！今天是她逃婚的日子啊！",
         "hit on sb 美式口语= 挑逗、搭讪某人；hit on an idea=忽然想到点子。",
         "Monica's Apartment", "hitting on"),

        ("buzz him in", "/bʌz ɪm ɪn/", "phrase 按门铃让他进", "B2", "weak_forms", ["生活词汇", "公寓"],
         "___! (按门禁让他进来)",
         "Buzz him in!",
         "快开门让他进来！",
         "公寓楼的intercom（门禁对讲机）发出buzz蜂鸣声 → buzz sb in = 按开门键放某人上楼。",
         "Monica's Apartment", "buzz him in"),

        ("Dear Diary moment", "/ˌdɪr ˈdaɪəri ˈmoʊmənt/", "n. phrase 值得写进日记的大事", "B2", "r_colored", ["习语", "幽默"],
         "Ooh, this is a ___.",
         "Ooh, this is a Dear Diary moment.",
         "哇哦，这可是值得写进日记的历史性时刻啊！",
         "Chandler式吐槽：Dear Diary… 相当于「我要把这天写进我的少女日记里」，故意煽情以制造幽默。",
         "Monica's Apartment", "Dear Diary moment"),

        ("brackety thing", "/ˈbrækəɾi θɪŋ/", "n. phrase（瞎编的）那个支架玩意儿", "B1", "flap_t", ["口语", "瞎编词汇"],
         "I'm supposed to attach a ___ to the side things.",
         "I'm supposed to attach a brackety thing to the side things.",
         "说明书说要把「那个支架玩意儿」装到「旁边那些玩意儿」上。",
         "Ross不知道零件名，在thing/things前加-y后缀瞎编：brackety=像bracket的东西，worm guys=螺丝钉（像小虫子）。",
         "Ross's Apartment", "brackety thing"),

        ("worm guys", "/wɝm ɡaɪz/", "n. phrase（瞎编的）螺丝小子们", "B1", "r_colored", ["口语", "幽默"],
         "using a bunch of these little ___.",
         "using a bunch of these little worm guys.",
         "用一堆这些小螺丝小子（不知道名字瞎叫的）。",
         "guy 可以指物，不一定是人，相当于「玩意儿」：the little guy=小家伙/小零件。",
         "Ross's Apartment", "worm guys"),

        ("outta here", "/ˈaʊɾə hɪr/", "contraction (out of here)", "A2", "flap_t", ["连读", "口语缩写"],
         "If you're gonna start with that stuff we're ___.",
         "If you're gonna start with that stuff we're outta here.",
         "你再絮叨这些有的没的我们就走人了啊！",
         "outta = out of；gonna = going to；都是美语日常快读的拼写。",
         "Ross's Apartment", "outta"),

        ("got screwed", "/ɡɑt skrud/", "phrase 被坑惨了", "B2", "vowel_ah", ["俚语", "情绪"],
         "You ___.",
         "You got screwed.",
         "你简直亏大了 / 你被坑得够惨。",
         "screw 作动词= screw（螺丝钉）拧进去 → 被screwed=被坑、被榨干；也可粗俗版。日常: I screwed up=我搞砸了。",
         "Ross's Apartment", "got screwed"),

        ("caught on", "/kɔt ɑn/", "phrasal verb 察觉、明白", "B2", "vowel_ah", ["phrasal_verb"],
         "I guess I should have ___ when she started going to the dentist.",
         "I guess I should have caught on when she started going to the dentist.",
         "她一周去四五次牙医的时候我就该看出来不对劲了。",
         "catch on = 理解、觉察；也可表流行：The song caught on quickly.（这首歌很快火了。）",
         "Restaurant", "caught on"),

        ("steer clear of you", "/stɪr klɪr əv ju/", "phrase 躲你远点儿", "B2", "r_colored", ["习语", "幽默"],
         "Ooh, ___!",
         "Ooh, steer clear of you!",
         "喔哟，那我可得离你远点！（你把男朋友浴巾都撕了啊）",
         "steer 掌舵 + clear of 避开 = 绕开某人/某事走。Steer clear of trouble=别惹麻烦。",
         "Restaurant", "steer clear of"),

        ("shredded", "/ˈʃrɛdɪd/", "v. 撕成碎片", "B2", "vowel_eh", ["动作", "CET6"],
         "I ___ my boyfriend's favorite bath towel.",
         "I shredded my boyfriend's favorite bath towel.",
         "我把我前男友最爱的浴巾给撕成了碎条。",
         "shred 碎条 → shred sth=切碎/撕成条；也可指健身练出的条状肌肉= shredded abs。",
         "Restaurant", "shredded"),

        ("cut me off", "/kʌt mi ɔf/", "phrasal verb 挂断我电话", "B2", "vowel_uh", ["phrasal_verb", "通讯"],
         "Hi, the machine ___ again…",
         "Hi, the machine cut me off again…",
         "喂，电话又把我给掐断了……",
         "cut sb off 还可以：切断供给、打断别人说话、道路截断。",
         "Monica's Apartment", "cut me off"),

        ("ripped your heart out", "/rɪpt jʊr hɑrt aʊt/", "phrase 把你心都撕烂了", "B2", "r_colored", ["习语", "情绪"],
         "Four years at the end of which she ___.",
         "Four years at the end of which she ripped your heart out.",
         "四年感情，到最后她把你心都撕碎了。",
         "rip=撕；rip one's heart out = 伤害极深。也可字面：rip the letter open. 撕开信。",
         "Ross's Apartment", "ripped your heart out"),

        ("Grab a spoon", "/ɡræb ə spun/", "phrase 拿起勺子=重新开始约会", "B2", "vowel_ae", ["经典金句", "隐喻"],
         "Welcome back to the world! ___!",
         "Welcome back to the world! Grab a spoon!",
         "欢迎回归单身大世界！赶紧「拿起勺子」（开撩冰淇淋妹子们）！",
         "Joey用冰淇淋口味比喻女人，Ross担心「一辈子只吃一种口味」，Joey让他Grab a spoon= 赶紧拿勺去挖吧=重新开始约。",
         "Ross's Apartment", "Grab a spoon"),

        ("flavors of ice cream", "/ˈfleɪvɚz əv ˈaɪs krim/", "n. 比喻 不同类型的女生", "B1", "r_colored", ["经典比喻"],
         "That's like saying there's only one ___ for you.",
         "That's like saying there's only one flavors of ice cream for you.",
         "说「一生只一个人」就好像在说「冰淇淋你只有一种口味」一样。",
         "Joey最精彩比喻：Rocky Road / Cookie Dough / Bing! Cherry Vanilla → 各种女生。",
         "Ross's Apartment", "flavors of ice cream"),

        ("a snap in his turtle", "/ə snæp ɪn hɪz ˈtɝɾəl/", "phrase （粗俗）他的小弟弟能重振雄风了", "B2", "r_colored", ["俚语", "Frannie梗"],
         "Before me, there was no ___ for two years.",
         "Before me, there was no snap in his turtle for two years.",
         "在我之前，他那玩意儿可是两年都没「弹」起来过哦。",
         "snap 啪一声 + turtle 乌龟（龟头缩进去）→ 委婉粗口。Frannie告诉Monica Paul根本不是阳痿，他是在骗炮。",
         "Iridium", "snap in his turtle"),

        ("was a line", "/wʌz ə laɪn/", "phrase 是一句撩妹的套话", "B2", "vowel_uh", ["俚语", "约会"],
         "Of course it ___!",
         "Of course it was a line!",
         "那当然是骗你上床的鬼话啊！你居然信！",
         "line在这里不是排队，是「套话/花言巧语」：pick-up line=搭讪开场白。",
         "Central Perk", "was a line"),

        ("beacon", "/ˈbikən/", "n. 信标、灯塔般的信号", "C1", "long_e", ["CET6", "比喻"],
         "Is it like I have some sort of ___ that only dogs and men can hear?",
         "Is it like I have some sort of beacon that only dogs and men with severe emotional problems can hear?",
         "难道我身上装了什么「感情问题男+狗」专用信标吗？专门吸渣男？",
         "灯塔beacon → 能吸引特定目标的信号源。Monica吐槽自己总是吸引感情有问题的男人。",
         "Central Perk", "beacon"),

        ("trained for nothing", "/treɪnd fɔr ˈnʌθɪŋ/", "phrase 什么技能都没学过", "B1", "r_colored", ["Rachel名言"],
         "I'm ___! I was laughed out of twelve interviews today.",
         "I'm trained for nothing! I was laughed out of twelve interviews today.",
         "我什么专业技能都没有！今天面了十二家，十二家都把我笑出来了。",
         "Rachel作为富家逃婚女，以前从来没工作过，大学=社交，所以啥也不会。这是她成长线起点。",
         "Central Perk", "trained for nothing"),

        ("laughed out of", "/læft aʊt əv/", "phrase 被轰着笑出来=面试惨败", "B2", "vowel_ae", ["习语"],
         "I was ___ twelve interviews today.",
         "I was laughed out of twelve interviews today.",
         "今天十二场面试，我都被人笑着给请了出去。",
         "laugh sb out of sth = 被嘲笑得自己呆不下去自己走了；非常生动的表达。",
         "Central Perk", "laughed out of"),

        ("upbeat", "/ˈʌpbit/", "adj. 乐观的、积极向上的", "B2", "long_e", ["情绪", "CET6"],
         "And yet you're surprisingly ___.",
         "And yet you're surprisingly upbeat.",
         "（十二场面试惨败）你居然还能这么嗨？",
         "upbeat 音乐节拍 upbeat=上拍 → 积极的、开心的。反义：downbeat=垂头丧气。",
         "Central Perk", "upbeat"),

        ("Sweet 'n' Lo", "/swit ən loʊ/", "n. 甜蜜低卡糖（代糖品牌名）", "B2", "o_diphthong", ["品牌", "生活"],
         "(to the waitress) ___?",
         "(to the waitress) Sweet 'n' Lo?",
         "（给服务员）给我来两包「甜又低」（代糖）？",
         "美国经典代糖品牌名，玩梗 Sweet + Low（低卡）= Sweet and Lo（故意拼写成Lo）。",
         "Monica's Apartment", "Sweet 'n' Lo"),

        ("kinda drifted", "/ˈkaɪndə ˈdrɪftɪd/", "phrase 有点疏远了", "B1", "schwa", ["kinda句型"],
         "You and I have ___ apart.",
         "You and I have kinda drifted apart.",
         "我知道我们俩这些年有点疏远了。",
         "kinda = kind of（有点）；sorta = sort of。口语中必须掌握的弱化词。",
         "Central Perk", "kinda drifted"),

        ("figure out", "/ˈfɪɡjɚ aʊt/", "phrasal verb 想明白、搞懂", "B1", "r_colored", ["phrasal_verb", "高频"],
         "Finally, I ___ I'd better answer it.",
         "Finally, I figure I'd better answer it.",
         "我最后想：我还是接一下电话吧。",
         "figure sth out = 搞清楚、想明白。高频得要死的短语动词，一定要吃透。",
         "Central Perk", "figure out"),

        ("cleansing my aura", "/ˈklɛnzɪŋ maɪ ˈɔrə/", "phrase 净化我的气场", "B2", "r_colored", ["Phoebe梗", "神秘学"],
         "Stop ___! No, just leave my aura alone, okay?",
         "Stop cleansing my aura! No, just leave my aura alone, okay?",
         "别净化我的气场了！就让我的气场「浑浊」着吧行吗！",
         "aura=气场/光环；New Age（新时代玄学）概念。Phoebe人设就是信玄学、按摩、水晶、前世。",
         "Central Perk", "cleansing my aura"),

        ("Be murky!", "/bi ˈmɝki/", "phrase 那就浑浊你的吧！", "B2", "r_colored", ["Phoebe名言"],
         "Phoebe: Fine! ___!",
         "Phoebe: Fine! Be murky!",
         "行！那你就一辈子糊里糊涂下去吧！（Phoebe气Ross不领情）",
         "murky=浑浊的、晦暗的。气场不清就murky；也可以说murky past=黑历史。",
         "Central Perk", "Be murky"),

        ("to hell with her", "/tu hɛl wɪð hɚ/", "phrase 让她去死吧/管她呢", "B1", "r_colored", ["情绪", "发泄"],
         "No I don't, ___! She left me!",
         "No I don't, to hell with her! She left me!",
         "才不祝她幸福，她爱咋咋地！她甩了我啊！",
         "to hell with X = 让X见鬼去吧！礼貌版：to heck with X。",
         "Central Perk", "to hell with her"),

        ("keep fixating on that", "/kip fɪkˈseɪɾɪŋ ɑn ðæt/", "phrase 老纠结这事", "B2", "flap_t", ["心理", "CET6"],
         "Why does everyone ___?",
         "Why does everyone keep fixating on that?",
         "为什么你们所有人都揪着这点（她是拉拉）不放？！",
         "fixate on sth =  obsessively focus on 死盯着不放。注意 fix / fixate 意思不同。",
         "Central Perk", "fixating on"),

        ("take it pretty well", "/teɪk ɪt ˈprɪɾi wɛl/", "phrase 接受得挺坦然、挺想得开", "B1", "flap_t", ["情绪", "高频词组"],
         "I told mom and dad last night, they seemed to ___.",
         "I told mom and dad last night, they seemed to take it pretty well.",
         "我昨晚跟爸妈说了，他们好像接受得挺平静。",
         "take sth well/badly = 对某事反应如何。Ross撒谎，其实他妈凌晨3点打电话嚎没孙子了。",
         "Central Perk", "take it pretty well"),

        ("hysterical", "/hɪˈstɛrɪkəl/", "adj. 歇斯底里的；极搞笑的", "B2", "vowel_eh", ["情绪", "多义词"],
         "So that ___ phone call I got from a woman sobbing at 3:00 A.M.",
         "So that hysterical phone call I got from a woman sobbing at 3:00 A.M.",
         "哦所以那通凌晨3点歇斯底里哭嚎说抱不上孙子的电话…打错了？",
         "hysterical 两个核心意思：1.情绪失控的；2.(口语)笑死我了=hysterical=hilarious。",
         "Central Perk", "hysterical"),

        ("have some hormones", "/hæv sʌm ˈhɔrmoʊnz/", "phrase 男人一点、拿出性欲来", "B2", "o_diphthong", ["Joey梗", "幽默"],
         "You're single! ___!",
         "You're single! Have some hormones!",
         "你单身了啊！发情啊！约啊！做点男人该做的事啊！",
         "hormone=荷尔蒙/激素。Joey粗暴逻辑：单身就该hormone满满出门撩妹。",
         "Monica's Apartment", "have some hormones"),

        ("a wrong number", "/ə rɔŋ ˈnʌmbɚ/", "n. 打错的电话", "A2", "r_colored", ["基础高频"],
         "What was that? A ___?",
         "What was that? A wrong number?",
         "那怎么回事？难道是打错了？（Monica拆Ross台）",
         "wrong number 打错电话；It's the wrong number.=你打错了。",
         "Central Perk", "wrong number"),

        ("survivor", "/sɚˈvaɪvɚ/", "n. 幸存者", "B2", "r_colored", ["CET4", "比喻"],
         "this is Rachel, another Lincoln High ___.",
         "this is Rachel, another Lincoln High survivor.",
         "各位这是Rachel，我们林肯高中的又一位「幸存者」（吐槽高中地狱）。",
         "survive 存活→survivor。这里是黑色幽默：把高中比作灾难，大家都是撑过来的survivor。",
         "Central Perk", "survivor"),

        ("four wet bridesmaids", "/fɔr wɛt ˈbraɪdzmeɪdz/", "n. phrase 四个浑身湿透的伴娘", "B1", "r_colored", ["Monica梗", "幽默"],
         "Or are we waiting for ___?",
         "Or are we waiting for four wet bridesmaids?",
         "你是打算现在说呢，还是等你那四个湿透的伴娘也赶过来再说？",
         "Rachel穿湿婚纱冲进来，Monica调侃：你那四个同样被雨淋透的伴娘啥时候到？",
         "Central Perk", "wet bridesmaids"),

        ("de-caff", "/di ˈkæf/", "n. 无咖啡因咖啡（decaf缩写）", "B2", "vowel_ae", ["生活词汇", "咖啡"],
         "Monica: (pointing at Rachel) ___.",
         "Monica: (pointing at Rachel) De-caff.",
         "Monica（对服务员指着Rachel）：给她无咖啡因的。（她已经够疯了别再加咖啡因）",
         "decaffeinated 去掉咖啡因的→口语decaf/di-caff。美国咖啡店必懂词：regular=普通的，decaf=脱因。",
         "Central Perk", "De-caff"),

        ("wondering", "/ˈwʌndɚɪŋ/", "v. 在琢磨、在纳闷", "A2", "r_colored", ["A2高频"],
         "and I started ___ 'Why am I doing this?'",
         "and I started wondering 'Why am I doing this?'",
         "然后我忽然开始想：我到底在干嘛？我到底是为谁在活？",
         "I wonder if/whether… 我想知道…；wondering 就是Rachel觉醒的起点。",
         "Monica's Apartment", "wondering"),

        ("a big pipe organ", "/ə bɪɡ paɪp ˈɔrɡən/", "n. phrase 大型管风琴", "B2", "r_colored", ["Monica肥皂剧梗"],
         "Now I'm guessing that he bought her the ___.",
         "Now I'm guessing that he bought her the big pipe organ.",
         "我押他给她买了个巨大的管风琴（肥皂剧剧情猜谜）。",
         "pipe organ 教堂管风琴。他们在看西班牙语肥皂剧，大家瞎猜剧情。",
         "Monica's Apartment", "pipe organ"),

        ("on a roll", "/ɑn ə roʊl/", "phrase 手气正顺、势如破竹", "B2", "o_diphthong", ["习语", "高频"],
         "Listen, while you're ___, if you feel like you gotta make a Western omelet…",
         "Listen, while you're on a roll, if you feel like you gotta make a Western omelet…",
         "既然你现在手气这么顺（第一次冲咖啡成功），要不顺手再做个西式欧姆蛋？",
         "on a roll = 连续成功、势头正好。Joey让Rachel做饭，结果咖啡难喝得被倒花盆里。",
         "Monica's Apartment", "on a roll"),

        ("Western omelet", "/ˈwɛstɚn ˈɑmlət/", "n. 西式洋葱火腿蛋卷", "B2", "vowel_ah", ["生活词汇", "食物"],
         "make a ___…",
         "make a Western omelet…",
         "做一份西式欧姆蛋（火腿洋葱青椒蛋卷）。",
         "omelet 蛋卷，也拼omelette。Western omelet=有火腿/洋葱/甜椒的经典款。",
         "Monica's Apartment", "Western omelet"),

        ("the barn raising scene in Witness", "/ðə bɑrn ˈreɪzɪŋ sin ɪn ˈwɪtnəs/", "phrase 《目击者》里集体建谷仓的经典温馨场面", "C1", "r_colored", ["电影梗", "Paul的夸张比喻"],
         "last night was like all my birthdays, both graduations, plus ___.",
         "last night was like umm, all my birthdays, both graduations, plus the barn raising scene in Witness.",
         "昨晚就好比我所有生日+两次毕业典礼+《证人》里全村人建谷仓的温馨名场面加起来那么爽！",
         "1985电影《Witness》哈里森福特主演，Amish村民集体帮主角搭建谷仓的经典温馨群戏。Paul极度夸张说法。",
         "Monica's Apartment", "barn raising scene in Witness"),

        ("input those numbers", "/ˈɪnpʊt ðoʊz ˈnʌmbɚz/", "phrase 把那些数字输进去", "B1", "o_diphthong", ["Chandler冷笑话"],
         "If I don't ___… it doesn't make much of a difference.",
         "If I don't input those numbers… it doesn't make much of a difference.",
         "我再不把那些数字敲进去……（其实干不干都没差别）。",
         "Chandler吐槽自己的工作：就是一堆无意义的数字录入（后期他自己也不知道自己干啥的梗）。",
         "Monica's Apartment", "input those numbers"),

        ("regional work", "/ˈridʒənəl wɝk/", "n. phrase 地方剧场演出（非百老汇）", "B2", "r_colored", ["Joey演员"],
         "Would I have seen you in anything? — I doubt it. Mostly ___.",
         "Would I have seen you in anything? — I doubt it. Mostly regional work.",
         "我看过你的剧吗？—— 应该没有，主要都是地方小剧场（跑龙套）。",
         "regional theater = 美国地方/地区剧场；百老汇=Broadway，外百老汇=Off-Broadway。",
         "Monica's Apartment", "regional work"),

        ("a real live boy", "/ə ˈriəl laɪv bɔɪ/", "phrase 一个真真正正的小男孩（匹诺曹梗）", "B2", "r_colored", ["文化梗", "匹诺曹"],
         "Chandler (sings): 'Once I was a wooden boy, a little wooden boy...'",
         "'Look, Gippetto, I'm a real live boy.'",
         "「看啊盖比特爷爷！我终于变成一个真正的小男孩了！」（Chandler黑Joey演过匹诺曹）",
         "匹诺曹经典台词。Gippetto=做木偶的老爷爷。Joey演过公园小剧场的Pinocchio。",
         "Monica's Apartment", "real live boy"),

        ("stop smiling", "/stɑp ˈsmaɪlɪŋ/", "phrase 别老傻笑了", "A1", "vowel_ah", ["高频词组"],
         "I can't ___.",
         "I can't stop smiling.",
         "我控制不住，我满脸都是笑。（Monica跟Paul睡了之后美滋滋）",
         "stop doing sth=停下做某事；stop to do=停下来去做。两者区别必考。",
         "Monica's Apartment", "stop smiling"),

        ("a hanger in your mouth", "/ə ˈhæŋɚ ɪn jʊr maʊθ/", "phrase 嘴里含了个衣架（形容咧嘴笑到僵）", "B2", "r_colored", ["Rachel比喻"],
         "You look like you slept with ___.",
         "You look like you slept with a hanger in your mouth.",
         "你那样子就好像睡觉时嘴里叼了个衣架被撑开在那儿笑。",
         "hanger 衣架；超级形象的毒舌比喻。Rachel损Monica也太会了。",
         "Monica's Apartment", "hanger in your mouth"),

        ("a little ahead of ourselves", "/ə ˈlɪɾəl əˈhɛd əv aʊrˈsɛlvz/", "phrase 步子迈太大、想太远了", "B2", "flap_t", ["习语", "高频"],
         "I think we are getting ___ here.",
         "I think we are getting a little ahead of ourselves here.",
         "我觉得我们想太远了吧（谈婚论嫁还早）。",
         "get ahead of oneself = 太早下结论、操之过急。比如考试还没考就在想放假，就是ahead of yourself。",
         "Monica's Apartment", "ahead of ourselves"),

        ("wish me luck", "/wɪʃ mi lʌk/", "phrase 祝我好运", "A2", "vowel_uh", ["高频"],
         "Oh, look, ___!",
         "Oh, look, wish me luck!",
         "快看快看，祝我好运！（Rachel准备出门找工作）",
         "wish sb luck = 祝某人好运；Good luck!= 好运！Break a leg!（演员圈）祝好运。",
         "Monica's Apartment", "wish me luck"),

        ("job things", "/dʒɑb θɪŋz/", "n. 那种叫「工作」的玩意儿", "A1", "vowel_ah", ["Rachel金句"],
         "I'm gonna go get one of those (Thinks) ___.",
         "I'm gonna go get one of those (Thinks) job things.",
         "我决定去弄一个那种……叫「工作」的东西。",
         "Rachel第一次意识到她需要找份工作。things=那个叫啥来着，很真实的口语。",
         "Monica's Apartment", "job things"),

        ("push my Aunt Roz through Parrot Jungle", "/pʊʃ maɪ ænt rɑz θru ˈpærət ˈdʒʌŋɡəl/", "phrase 推着轮椅上的Roz阿姨逛鹦鹉丛林乐园", "B2", "vowel_ae", ["Florida梗", "Frannie"],
         "I'm ___ and you're having sex!",
         "I'm pushing my Aunt Roz through Parrot Jungle and you're having sex!",
         "我在佛罗里达推着Roz阿姨逛鹦鹉乐园呢，你却在床上爽？不公平啊！",
         "Parrot Jungle（现在叫Jungle Island）是迈阿密著名热带鸟园。推老人逛公园 vs 泡汉子的反差。",
         "Iridium", "Parrot Jungle"),

        ("take credit for Paul", "/teɪk ˈkrɛdɪt fɔr pɔl/", "phrase 把Paul的改变归功于我", "B2", "r_colored", ["高频词组"],
         "I ___ Paul. Y'know before me, there was no snap in his turtle.",
         "I take credit for Paul. Y'know before me, there was no snap in his turtle.",
         "Paul的「重振雄风」那得归功于我，在我之前他两年都不行。",
         "take credit for X = 把X功劳揽在自己身上；give credit = 承认某人的功劳。",
         "Iridium", "take credit for"),

        ("severe emotional problems", "/səˈvɪr ɪˈmoʊʃənəl ˈprɑbləmz/", "phrase 严重的情感问题", "B2", "o_diphthong", ["Monica自嘲"],
         "a beacon that only dogs and men with ___ can hear?",
         "a beacon that only dogs and men with severe emotional problems can hear?",
         "就好像我自带雷达，只招狗和有严重情感创伤的男人？",
         "severe=严重的；emotional problems=感情/心理问题。Monica自嘲渣男吸引体质。",
         "Central Perk", "emotional problems"),

        ("on sale", "/ɑn seɪl/", "phrase 打折出售中", "A2", "o_diphthong", ["购物高频"],
         "I found John and David boots ___, fifty percent off!",
         "I found John and David boots on sale, fifty percent off!",
         "我撞见John & David的靴子打折！半价！太爽了！",
         "on sale 打折中（美）；for sale 出售中；50% off = 打五折。",
         "Central Perk", "on sale"),

        ("fifty percent off", "/ˈfɪfti pɚˈsɛnt ɔf/", "phrase 打五折", "A2", "r_colored", ["购物数字"],
         "John and David boots on sale, ___!",
         "John and David boots on sale, fifty percent off!",
         "John & David靴子打折半价，就被我给捡到了！",
         "X% off = 去掉X%=100-X折。20% off = 八折。Rachel靠购物疗愈面试惨败。",
         "Central Perk", "fifty percent off"),

    ]

    cards = []
    for i, (target_word, ipa, pos, level, pronunciation_focus, tags,
            sentence_cloze, sentence_full, translation,
            cultural_note, scene_kw, search_substr) in enumerate(cards_raw, start=1):
        scene_id, line_index, character, _ = find_line(scene_kw, search_substr)
        # Map screenshot: some scenes may not have a screenshot; fall back to placeholder
        screenshot = f"/episodes/S01E01/images/{scene_id}.png"
        cards.append({
            "id": f"S01E01_{i:03d}",
            "episode": "S01E01",
            "scene_id": scene_id,
            "line_index": line_index,
            "character": character,
            "target_word": target_word,
            "ipa": ipa,
            "pos": pos,
            "level": level,
            "pronunciation_focus": pronunciation_focus,
            "tags": tags,
            "sentence_cloze": sentence_cloze,
            "sentence_full": sentence_full,
            "translation": translation,
            "cultural_note": cultural_note,
            "screenshot": screenshot,
            "frequency_rank": None,
        })
    return cards


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    root = Path(__file__).resolve().parent.parent
    rtf_path = root.parent / "0001  Monica Gets a New Roommate - La moglie mancata S1-D1-A.rtf"
    out_dir = root / "public" / "episodes" / "S01E01"
    src_data_dir = root / "src" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    src_data_dir.mkdir(parents=True, exist_ok=True)

    if not rtf_path.exists():
        print(f"ERROR: RTF not found: {rtf_path}", file=sys.stderr)
        return 1

    raw = rtf_path.read_text(encoding="cp1252", errors="replace")
    plain = strip_rtf(raw)
    parsed = parse_script(plain)

    metadata = parsed["metadata"]
    scenes = parsed["scenes"]

    script_out = []
    for s in scenes:
        for ln in s["lines"]:
            item = {"scene_id": s["scene_id"], "scene_name": s["scene_name"], **ln}
            script_out.append(item)

    cards = build_cards(scenes)

    # Write JSON
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "script.json").write_text(json.dumps(script_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also put a copy under src/data so TS can import directly without fetch
    (src_data_dir / "S01E01_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    (src_data_dir / "S01E01_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (src_data_dir / "S01E01_script.json").write_text(json.dumps(script_out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[OK] metadata.json  -> {} chars, {} scenes".format(len(metadata['characters']), metadata['scenes_count']))
    print("[OK] script.json    -> {} lines".format(len(script_out)))
    print("[OK] cards.json     -> {} flashcards".format(len(cards)))
    print("   output: {}".format(out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
