"""
English Noun Etymology Dictionary
==================================
Common etymology patterns for English nouns from Friends S01E01.

Format: {noun_lower: {"translation": "中文", "breakdown": [{"part": "...", "origin": "...", "meaning": "..."}]}}
"""

ETYMOLOGY_DICT = {
    # ---- A ----
    "actor": {
        "translation": "演员",
        "breakdown": [
            {"part": "act-", "origin": "拉丁语 agere", "meaning": "做，行动"},
            {"part": "-or", "origin": "施动者后缀（拉丁语 -tor）", "meaning": "做...的人"},
        ]
    },
    "air": {
        "translation": "空气",
        "breakdown": [
            {"part": "air", "origin": "古法语 air / 拉丁语 aer", "meaning": "空气（来自希腊语 ἀήρ）"},
        ]
    },
    "airplane": {
        "translation": "飞机",
        "breakdown": [
            {"part": "air", "origin": "空气", "meaning": "空中"},
            {"part": "plane", "origin": "拉丁语 planum", "meaning": "平面"},
        ]
    },
    "answer": {
        "translation": "回答",
        "breakdown": [
            {"part": "an-", "origin": "古英语 and-", "meaning": "反对，回应"},
            {"part": "swer", "origin": "古英语 swerian", "meaning": "发誓，承诺"},
        ]
    },
    "apartment": {
        "translation": "公寓",
        "breakdown": [
            {"part": "apart-", "origin": "拉丁语 ad + partem", "meaning": "分开，分离"},
            {"part": "-ment", "origin": "名词后缀（来自法语 -ment）", "meaning": "表示状态/结果"},
        ]
    },
    "arm": {
        "translation": "手臂；武器",
        "breakdown": [
            {"part": "arm", "origin": "古英语 earm / 拉丁语 armus", "meaning": "手臂，肩膀"},
        ]
    },
    "art": {
        "translation": "艺术",
        "breakdown": [
            {"part": "art", "origin": "拉丁语 ars / artem", "meaning": "技艺，技能"},
        ]
    },
    "aunt": {
        "translation": "阿姨，姑妈",
        "breakdown": [
            {"part": "aunt", "origin": "古法语 ante / 拉丁语 amita", "meaning": "父亲的姐妹"},
        ]
    },
    
    # ---- B ----
    "bath": {
        "translation": "洗澡，浴室",
        "breakdown": [
            {"part": "bath", "origin": "古英语 bæð", "meaning": "浸泡，清洗"},
        ]
    },
    "bed": {
        "translation": "床",
        "breakdown": [
            {"part": "bed", "origin": "古英语 bedd", "meaning": "花园苗床，睡觉的地方"},
        ]
    },
    "bedroom": {
        "translation": "卧室",
        "breakdown": [
            {"part": "bed", "origin": "床", "meaning": "睡觉"},
            {"part": "room", "origin": "古英语 rum", "meaning": "空间，房间"},
        ]
    },
    "beer": {
        "translation": "啤酒",
        "breakdown": [
            {"part": "beer", "origin": "古英语 beor", "meaning": "啤酒（可能来自拉丁语 bibere 喝）"},
        ]
    },
    "birthday": {
        "translation": "生日",
        "breakdown": [
            {"part": "birth", "origin": "古英语 byrth", "meaning": "出生"},
            {"part": "day", "origin": "古英语 dæg", "meaning": "天"},
        ]
    },
    
    # ---- C ----
    "car": {
        "translation": "汽车",
        "breakdown": [
            {"part": "car", "origin": "中古英语 carre / 古北法语 car", "meaning": "四轮马车"},
        ]
    },
    "coffee": {
        "translation": "咖啡",
        "breakdown": [
            {"part": "coff-", "origin": "土耳其语 kahve / 阿拉伯语 qahwa", "meaning": "咖啡"},
            {"part": "-ee", "origin": "法语 -é", "meaning": "名词后缀"},
        ]
    },
    "cold": {
        "translation": "寒冷；感冒",
        "breakdown": [
            {"part": "cold", "origin": "古英语 cald", "meaning": "冷的"},
        ]
    },
    "couch": {
        "translation": "沙发",
        "breakdown": [
            {"part": "couch", "origin": "古法语 coucher", "meaning": "躺下（来自拉丁语 collocāre 放置）"},
        ]
    },
    
    # ---- D ----
    "date": {
        "translation": "约会；日期",
        "breakdown": [
            {"part": "date", "origin": "拉丁语 data", "meaning": "给予（指书信上标注的日期）"},
        ]
    },
    "doctor": {
        "translation": "医生；博士",
        "breakdown": [
            {"part": "doct-", "origin": "拉丁语 docēre", "meaning": "教"},
            {"part": "-or", "origin": "施动者后缀", "meaning": "做...的人"},
        ]
    },
    
    # ---- E ----
    "egg": {
        "translation": "蛋",
        "breakdown": [
            {"part": "egg", "origin": "古英语 æg", "meaning": "蛋"},
        ]
    },
    
    # ---- F ----
    "family": {
        "translation": "家庭",
        "breakdown": [
            {"part": "famili-", "origin": "拉丁语 familia", "meaning": "家庭，仆人"},
            {"part": "-y", "origin": "名词后缀", "meaning": "表示集合/状态"},
        ]
    },
    "friend": {
        "translation": "朋友",
        "breakdown": [
            {"part": "friend", "origin": "古英语 frēond", "meaning": "爱人，朋友（来自 frēon 爱）"},
        ]
    },
    
    # ---- G ----
    "girl": {
        "translation": "女孩",
        "breakdown": [
            {"part": "girl", "origin": "中古英语 girle", "meaning": "孩子（性别不明）"},
        ]
    },
    
    # ---- H ----
    "home": {
        "translation": "家",
        "breakdown": [
            {"part": "home", "origin": "古英语 hām", "meaning": "村庄，住所"},
        ]
    },
    "house": {
        "translation": "房子",
        "breakdown": [
            {"part": "house", "origin": "古英语 hūs", "meaning": "遮蔽处，住所"},
        ]
    },
    
    # ---- J ----
    "job": {
        "translation": "工作",
        "breakdown": [
            {"part": "job", "origin": "中古英语 jobbe", "meaning": "一块工作"},
        ]
    },
    
    # ---- K ----
    "key": {
        "translation": "钥匙；关键",
        "breakdown": [
            {"part": "key", "origin": "古英语 cǣg", "meaning": "钥匙"},
        ]
    },
    
    # ---- L ----
    "life": {
        "translation": "生命，生活",
        "breakdown": [
            {"part": "life", "origin": "古英语 lif", "meaning": "生命"},
        ]
    },
    "love": {
        "translation": "爱",
        "breakdown": [
            {"part": "love", "origin": "古英语 lufu", "meaning": "爱，喜爱"},
        ]
    },
    
    # ---- M ----
    "man": {
        "translation": "男人",
        "breakdown": [
            {"part": "man", "origin": "古英语 mann", "meaning": "人（不限性别）"},
        ]
    },
    "money": {
        "translation": "钱",
        "breakdown": [
            {"part": "mon-", "origin": "拉丁语 monēta", "meaning": "铸币厂（Juno Moneta 神庙）"},
            {"part": "-ey", "origin": "法语 -ie", "meaning": "名词后缀"},
        ]
    },
    "mother": {
        "translation": "母亲",
        "breakdown": [
            {"part": "moth-", "origin": "古英语 mōdor", "meaning": "母亲"},
            {"part": "-er", "origin": "亲属关系后缀", "meaning": "表示人"},
        ]
    },
    
    # ---- N ----
    "night": {
        "translation": "夜晚",
        "breakdown": [
            {"part": "night", "origin": "古英语 niht", "meaning": "夜"},
        ]
    },
    
    # ---- P ----
    "party": {
        "translation": "派对；聚会",
        "breakdown": [
            {"part": "part-", "origin": "拉丁语 pars / partis", "meaning": "部分，一方"},
            {"part": "-y", "origin": "法语 -ie", "meaning": "名词后缀"},
        ]
    },
    "phone": {
        "translation": "电话",
        "breakdown": [
            {"part": "phon-", "origin": "希腊语 φωνή (phōnē)", "meaning": "声音"},
            {"part": "-e", "origin": "telephone 的缩写", "meaning": "省略前缀 tele-"},
        ]
    },
    
    # ---- R ----
    "ring": {
        "translation": "戒指；铃声",
        "breakdown": [
            {"part": "ring", "origin": "古英语 hring", "meaning": "环形物"},
        ]
    },
    
    # ---- S ----
    "shower": {
        "translation": "淋浴",
        "breakdown": [
            {"part": "show-", "origin": "古英语 scūr", "meaning": "阵雨"},
            {"part": "-er", "origin": "工具/地点后缀", "meaning": "产生...的东西"},
        ]
    },
    "sister": {
        "translation": "姐妹",
        "breakdown": [
            {"part": "sist-", "origin": "古英语 sweostor", "meaning": "姐妹"},
            {"part": "-er", "origin": "亲属关系后缀", "meaning": "表示人"},
        ]
    },
    
    # ---- T ----
    "tea": {
        "translation": "茶",
        "breakdown": [
            {"part": "tea", "origin": "闽南语 tê / 汉语 茶", "meaning": "茶叶"},
        ]
    },
    "time": {
        "translation": "时间",
        "breakdown": [
            {"part": "time", "origin": "古英语 tīma", "meaning": "有限的时间段"},
        ]
    },
    
    # ---- W ----
    "water": {
        "translation": "水",
        "breakdown": [
            {"part": "wat-", "origin": "古英语 wæter", "meaning": "水"},
            {"part": "-er", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "wedding": {
        "translation": "婚礼",
        "breakdown": [
            {"part": "wed-", "origin": "古英语 wedd", "meaning": "誓言，契约"},
            {"part": "-ing", "origin": "动名词后缀", "meaning": "表示动作/事件"},
        ]
    },
    "wife": {
        "translation": "妻子",
        "breakdown": [
            {"part": "wife", "origin": "古英语 wīf", "meaning": "女人，妻子"},
        ]
    },
    "woman": {
        "translation": "女人",
        "breakdown": [
            {"part": "wo-", "origin": "古英语 wīf", "meaning": "女人"},
            {"part": "man", "origin": "古英语 mann", "meaning": "人"},
        ]
    },
    "work": {
        "translation": "工作",
        "breakdown": [
            {"part": "work", "origin": "古英语 weorc", "meaning": "劳动，作品"},
        ]
    },

    # ---- Additional common words ----
    # A
    "anything": {
        "translation": "任何事物",
        "breakdown": [
            {"part": "any-", "origin": "古英语 ænig", "meaning": "任何"},
            {"part": "thing", "origin": "古英语 þing", "meaning": "事物，集会"},
        ]
    },
    "anybody": {
        "translation": "任何人",
        "breakdown": [
            {"part": "any-", "origin": "古英语 ænig", "meaning": "任何"},
            {"part": "body", "origin": "古英语 bodig", "meaning": "身体，人"},
        ]
    },
    "aura": {
        "translation": "气场，氛围",
        "breakdown": [
            {"part": "aura", "origin": "拉丁语 aura / 希腊语 αὔρα", "meaning": "微风，气息"},
        ]
    },
    "authority": {
        "translation": "权威，权力",
        "breakdown": [
            {"part": "author-", "origin": "拉丁语 auctor", "meaning": "创造者，发起者"},
            {"part": "-ity", "origin": "拉丁语 -itas", "meaning": "名词后缀，表示状态"},
        ]
    },
    # B
    "boat": {
        "translation": "船",
        "breakdown": [
            {"part": "boat", "origin": "古英语 bāt", "meaning": "小船"},
        ]
    },
    "bookcase": {
        "translation": "书架，书柜",
        "breakdown": [
            {"part": "book", "origin": "古英语 bōc", "meaning": "书"},
            {"part": "case", "origin": "拉丁语 capsa", "meaning": "容器，盒子"},
        ]
    },
    "boy": {
        "translation": "男孩",
        "breakdown": [
            {"part": "boy", "origin": "中古英语 boy", "meaning": "男仆，男孩（来源不明）"},
        ]
    },
    "boyfriend": {
        "translation": "男朋友",
        "breakdown": [
            {"part": "boy", "origin": "男孩", "meaning": "男性"},
            {"part": "friend", "origin": "古英语 frēond", "meaning": "朋友，爱人"},
        ]
    },
    "break": {
        "translation": "休息；打破",
        "breakdown": [
            {"part": "break", "origin": "古英语 brecan", "meaning": "破碎，中断"},
        ]
    },
    "brother": {
        "translation": "兄弟",
        "breakdown": [
            {"part": "broth-", "origin": "古英语 brōþor", "meaning": "兄弟"},
            {"part": "-er", "origin": "亲属关系后缀", "meaning": "表示人"},
        ]
    },
    "building": {
        "translation": "建筑物",
        "breakdown": [
            {"part": "build-", "origin": "古英语 byldan", "meaning": "建造"},
            {"part": "-ing", "origin": "动名词后缀", "meaning": "表示动作结果"},
        ]
    },
    "bunch": {
        "translation": "一串，一群",
        "breakdown": [
            {"part": "bunch", "origin": "古法语 bunch / boche", "meaning": "肿块，凸起"},
        ]
    },
    # C
    "call": {
        "translation": "电话；呼叫",
        "breakdown": [
            {"part": "call", "origin": "古英语 ceallian", "meaning": "大声喊叫"},
        ]
    },
    "card": {
        "translation": "卡片",
        "breakdown": [
            {"part": "card", "origin": "拉丁语 charta / 希腊语 χάρτης", "meaning": "纸，纸张"},
        ]
    },
    "case": {
        "translation": "情况；箱子",
        "breakdown": [
            {"part": "case", "origin": "拉丁语 capsa", "meaning": "容器，盒子"},
        ]
    },
    "chance": {
        "translation": "机会",
        "breakdown": [
            {"part": "chance", "origin": "古法语 cheance", "meaning": "偶然，运气（来自拉丁语 cadere 落下）"},
        ]
    },
    "cherry": {
        "translation": "樱桃",
        "breakdown": [
            {"part": "cherry", "origin": "古法语 cerise / 拉丁语 cerasum", "meaning": "樱桃（来自希腊语 κεράσιον）"},
        ]
    },
    "city": {
        "translation": "城市",
        "breakdown": [
            {"part": "cit-", "origin": "古法语 cite / 拉丁语 civitas", "meaning": "公民，城市"},
            {"part": "-y", "origin": "名词后缀", "meaning": "表示状态/地方"},
        ]
    },
    "closeness": {
        "translation": "亲密，接近",
        "breakdown": [
            {"part": "close", "origin": "拉丁语 clausus", "meaning": "关闭，接近"},
            {"part": "-ness", "origin": "古英语 -nes", "meaning": "名词后缀，表示状态"},
        ]
    },
    "come": {
        "translation": "来",
        "breakdown": [
            {"part": "come", "origin": "古英语 cuman", "meaning": "来，到达"},
        ]
    },
    "commercial": {
        "translation": "广告；商业的",
        "breakdown": [
            {"part": "com-", "origin": "拉丁语 com-", "meaning": "共同"},
            {"part": "merc-", "origin": "拉丁语 merx", "meaning": "商品"},
            {"part": "-ial", "origin": "形容词后缀", "meaning": "与...有关的"},
        ]
    },
    "control": {
        "translation": "控制",
        "breakdown": [
            {"part": "con-", "origin": "拉丁语 con-", "meaning": "共同"},
            {"part": "trol", "origin": "古法语 contrerôle", "meaning": "对照登记簿"},
        ]
    },
    # D
    # E
    "egg": {
        "translation": "蛋",
        "breakdown": [
            {"part": "egg", "origin": "古英语 æg", "meaning": "蛋"},
        ]
    },
    "idea": {
        "translation": "想法，主意",
        "breakdown": [
            {"part": "idea", "origin": "希腊语 ἰδέα (idéa)", "meaning": "形式，外观（来自 idein 看）"},
        ]
    },
    "idiot": {
        "translation": "傻瓜，白痴",
        "breakdown": [
            {"part": "idiot", "origin": "希腊语 ἰδιώτης (idiōtēs)", "meaning": "普通人，非专业人士"},
        ]
    },
    "image": {
        "translation": "图像，形象",
        "breakdown": [
            {"part": "image", "origin": "拉丁语 imago", "meaning": "复制品，肖像"},
        ]
    },
    "independence": {
        "translation": "独立",
        "breakdown": [
            {"part": "in-", "origin": "拉丁语 in-", "meaning": "不，非"},
            {"part": "depend-", "origin": "拉丁语 dependēre", "meaning": "悬挂于，依赖"},
            {"part": "-ence", "origin": "名词后缀", "meaning": "表示状态"},
        ]
    },
    "intestine": {
        "translation": "肠",
        "breakdown": [
            {"part": "intes-", "origin": "拉丁语 intestinum", "meaning": "内部的"},
            {"part": "-ine", "origin": "形容词/名词后缀", "meaning": "与...有关的"},
        ]
    },
    "issue": {
        "translation": "问题；议题",
        "breakdown": [
            {"part": "issue", "origin": "古法语 issue", "meaning": "出口，结果（来自拉丁语 exire 出去）"},
        ]
    },
    # F
    # G
    # H
    # I
    # J
    "joint": {
        "translation": "关节；场所",
        "breakdown": [
            {"part": "joint", "origin": "古法语 joint / 拉丁语 junctus", "meaning": "连接，结合"},
        ]
    },
    # K
    "kind": {
        "translation": "种类；善良的",
        "breakdown": [
            {"part": "kind", "origin": "古英语 cynd", "meaning": "自然，种类"},
        ]
    },
    # L
    "leg": {
        "translation": "腿",
        "breakdown": [
            {"part": "leg", "origin": "古北欧语 leggr", "meaning": "腿，肢体"},
        ]
    },
    "lesbian": {
        "translation": "女同性恋",
        "breakdown": [
            {"part": "lesbian", "origin": "希腊语 Lesbos（莱斯博斯岛）", "meaning": "诗人萨福的故乡"},
        ]
    },
    "library": {
        "translation": "图书馆",
        "breakdown": [
            {"part": "libr-", "origin": "拉丁语 liber", "meaning": "书"},
            {"part": "-ary", "origin": "拉丁语 -arium", "meaning": "与...有关的地方"},
        ]
    },
    "line": {
        "translation": "线；台词",
        "breakdown": [
            {"part": "line", "origin": "拉丁语 linea", "meaning": "亚麻线，线条"},
        ]
    },
    "lot": {
        "translation": "许多；命运",
        "breakdown": [
            {"part": "lot", "origin": "古英语 hlot", "meaning": "抽签，命运"},
        ]
    },
    "luck": {
        "translation": "运气",
        "breakdown": [
            {"part": "luck", "origin": "中古低地德语 lucke", "meaning": "好运"},
        ]
    },
    # M
    "machine": {
        "translation": "机器",
        "breakdown": [
            {"part": "machine", "origin": "法语 machine / 拉丁语 machina", "meaning": "装置，器械（来自希腊语 μηχανή）"},
        ]
    },
    "matrimony": {
        "translation": "婚姻",
        "breakdown": [
            {"part": "matri-", "origin": "拉丁语 mater", "meaning": "母亲"},
            {"part": "-mony", "origin": "拉丁语 -monium", "meaning": "状态，行为"},
        ]
    },
    "mess": {
        "translation": "混乱；一团糟",
        "breakdown": [
            {"part": "mess", "origin": "古法语 mes", "meaning": "一份食物，一道菜"},
        ]
    },
    "metaphor": {
        "translation": "隐喻，比喻",
        "breakdown": [
            {"part": "meta-", "origin": "希腊语 μετά", "meaning": "超越，之后"},
            {"part": "-phor", "origin": "希腊语 φορά", "meaning": "携带，转移"},
        ]
    },
    "middle": {
        "translation": "中间",
        "breakdown": [
            {"part": "mid-", "origin": "古英语 midd", "meaning": "中间"},
            {"part": "-dle", "origin": "古英语 -del", "meaning": "名词后缀"},
        ]
    },
    "moment": {
        "translation": "时刻，瞬间",
        "breakdown": [
            {"part": "moment", "origin": "拉丁语 momentum", "meaning": "运动，重要性"},
        ]
    },
    "morning": {
        "translation": "早晨",
        "breakdown": [
            {"part": "morn-", "origin": "古英语 morgen", "meaning": "早晨"},
            {"part": "-ing", "origin": "名词后缀", "meaning": "表示时间"},
        ]
    },
    "mouth": {
        "translation": "嘴",
        "breakdown": [
            {"part": "mouth", "origin": "古英语 mūþ", "meaning": "嘴，开口"},
        ]
    },
    # N
    "name": {
        "translation": "名字",
        "breakdown": [
            {"part": "name", "origin": "古英语 nama", "meaning": "名字"},
        ]
    },
    "neck": {
        "translation": "脖子",
        "breakdown": [
            {"part": "neck", "origin": "古英语 hnecca", "meaning": "脖子，后颈"},
        ]
    },
    "nothing": {
        "translation": "没有什么",
        "breakdown": [
            {"part": "no-", "origin": "古英语 nā", "meaning": "不，无"},
            {"part": "thing", "origin": "古英语 þing", "meaning": "事物"},
        ]
    },
    "number": {
        "translation": "数字，号码",
        "breakdown": [
            {"part": "numb-", "origin": "古法语 nombre / 拉丁语 numerus", "meaning": "数量"},
            {"part": "-er", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    # O
    "omelet": {
        "translation": "煎蛋卷",
        "breakdown": [
            {"part": "omelet", "origin": "法语 omelette", "meaning": "煎蛋（来自拉丁语 lamella 薄片）"},
        ]
    },
    "organ": {
        "translation": "器官；风琴",
        "breakdown": [
            {"part": "organ", "origin": "希腊语 ὄργανον (organon)", "meaning": "工具，器官"},
        ]
    },
    # P
    "pain": {
        "translation": "疼痛；痛苦",
        "breakdown": [
            {"part": "pain", "origin": "古法语 peine / 拉丁语 poena", "meaning": "惩罚，痛苦"},
        ]
    },
    "parachute": {
        "translation": "降落伞",
        "breakdown": [
            {"part": "para-", "origin": "法语 para-", "meaning": "防御，对抗"},
            {"part": "-chute", "origin": "法语 chute", "meaning": "落下"},
        ]
    },
    "park": {
        "translation": "公园",
        "breakdown": [
            {"part": "park", "origin": "古法语 parc", "meaning": "围起来的区域"},
        ]
    },
    "part": {
        "translation": "部分",
        "breakdown": [
            {"part": "part", "origin": "拉丁语 pars / partis", "meaning": "部分，份额"},
        ]
    },
    "people": {
        "translation": "人们",
        "breakdown": [
            {"part": "people", "origin": "古法语 peuple / 拉丁语 populus", "meaning": "人民"},
        ]
    },
    "percent": {
        "translation": "百分比",
        "breakdown": [
            {"part": "per-", "origin": "拉丁语 per", "meaning": "每"},
            {"part": "-cent", "origin": "拉丁语 centum", "meaning": "一百"},
        ]
    },
    "person": {
        "translation": "人",
        "breakdown": [
            {"part": "person", "origin": "拉丁语 persona", "meaning": "面具，角色"},
        ]
    },
    "pigeon": {
        "translation": "鸽子",
        "breakdown": [
            {"part": "pigeon", "origin": "古法语 pijon", "meaning": "幼鸽（来自拉丁语 pipio 小鸟叫声）"},
        ]
    },
    "pipe": {
        "translation": "管子；烟斗",
        "breakdown": [
            {"part": "pipe", "origin": "古英语 pīpe", "meaning": "管子（来自拉丁语 pipare 发出声音）"},
        ]
    },
    "point": {
        "translation": "点；要点",
        "breakdown": [
            {"part": "point", "origin": "古法语 point / 拉丁语 punctum", "meaning": "刺，点"},
        ]
    },
    "port": {
        "translation": "港口",
        "breakdown": [
            {"part": "port", "origin": "拉丁语 portus", "meaning": "港口，避风处"},
        ]
    },
    "potato": {
        "translation": "土豆",
        "breakdown": [
            {"part": "potato", "origin": "西班牙语 patata / 泰诺语 batata", "meaning": "甜薯"},
        ]
    },
    "prison": {
        "translation": "监狱",
        "breakdown": [
            {"part": "pris-", "origin": "古法语 pris / 拉丁语 prehendere", "meaning": "抓住"},
            {"part": "-on", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "production": {
        "translation": "生产；制作",
        "breakdown": [
            {"part": "pro-", "origin": "拉丁语 pro-", "meaning": "向前"},
            {"part": "duct-", "origin": "拉丁语 ducere", "meaning": "引导，带领"},
            {"part": "-ion", "origin": "名词后缀", "meaning": "表示动作/结果"},
        ]
    },
    "purse": {
        "translation": "钱包；手提包",
        "breakdown": [
            {"part": "purse", "origin": "古英语 purs", "meaning": "钱袋"},
        ]
    },
    # Q
    "question": {
        "translation": "问题",
        "breakdown": [
            {"part": "quest-", "origin": "拉丁语 quaerere", "meaning": "询问，寻求"},
            {"part": "-ion", "origin": "名词后缀", "meaning": "表示动作"},
        ]
    },
    # R
    "relationship": {
        "translation": "关系",
        "breakdown": [
            {"part": "re-", "origin": "拉丁语 re-", "meaning": "回，再"},
            {"part": "lat-", "origin": "拉丁语 latus", "meaning": "携带"},
            {"part": "-ion", "origin": "名词后缀", "meaning": "表示动作"},
            {"part": "-ship", "origin": "古英语 -scipe", "meaning": "状态，关系"},
        ]
    },
    "revelation": {
        "translation": "启示，揭露",
        "breakdown": [
            {"part": "re-", "origin": "拉丁语 re-", "meaning": "回"},
            {"part": "vel-", "origin": "拉丁语 velare", "meaning": "遮盖"},
            {"part": "-ation", "origin": "名词后缀", "meaning": "表示动作/结果"},
        ]
    },
    "road": {
        "translation": "路",
        "breakdown": [
            {"part": "road", "origin": "古英语 rād", "meaning": "骑行，旅程"},
        ]
    },
    "roll": {
        "translation": "卷；面包卷",
        "breakdown": [
            {"part": "roll", "origin": "古法语 role / 拉丁语 rotulus", "meaning": "小轮子，卷"},
        ]
    },
    "room": {
        "translation": "房间",
        "breakdown": [
            {"part": "room", "origin": "古英语 rum", "meaning": "空间，开阔的地方"},
        ]
    },
    "rule": {
        "translation": "规则",
        "breakdown": [
            {"part": "rule", "origin": "古法语 riule / 拉丁语 regula", "meaning": "直尺，规则"},
        ]
    },
    # S
    "sale": {
        "translation": "出售，销售",
        "breakdown": [
            {"part": "sale", "origin": "古英语 sala", "meaning": "出售（来自 sellan 给予）"},
        ]
    },
    "scene": {
        "translation": "场景；场面",
        "breakdown": [
            {"part": "scene", "origin": "拉丁语 scaena / 希腊语 σκηνή", "meaning": "舞台，帐篷"},
        ]
    },
    "school": {
        "translation": "学校",
        "breakdown": [
            {"part": "school", "origin": "古英语 scōl / 拉丁语 schola", "meaning": "闲暇，学习的地方（来自希腊语 σχολή）"},
        ]
    },
    "sex": {
        "translation": "性；性别",
        "breakdown": [
            {"part": "sex", "origin": "拉丁语 sexus", "meaning": "性别（来源不确定）"},
        ]
    },
    "shoe": {
        "translation": "鞋",
        "breakdown": [
            {"part": "shoe", "origin": "古英语 scōh", "meaning": "鞋"},
        ]
    },
    "side": {
        "translation": "边，侧面",
        "breakdown": [
            {"part": "side", "origin": "古英语 sīde", "meaning": "侧面，边"},
        ]
    },
    "something": {
        "translation": "某事物",
        "breakdown": [
            {"part": "some-", "origin": "古英语 sum", "meaning": "某个"},
            {"part": "thing", "origin": "古英语 þing", "meaning": "事物"},
        ]
    },
    "someone": {
        "translation": "某人",
        "breakdown": [
            {"part": "some-", "origin": "古英语 sum", "meaning": "某个"},
            {"part": "one", "origin": "古英语 ān", "meaning": "一，一个"},
        ]
    },
    "sort": {
        "translation": "种类；排序",
        "breakdown": [
            {"part": "sort", "origin": "古法语 sorte / 拉丁语 sors", "meaning": "命运，种类"},
        ]
    },
    "sound": {
        "translation": "声音",
        "breakdown": [
            {"part": "sound", "origin": "古法语 son / 拉丁语 sonus", "meaning": "声音"},
        ]
    },
    "spoon": {
        "translation": "勺子",
        "breakdown": [
            {"part": "spoon", "origin": "古英语 spōn", "meaning": "木片，芯片"},
        ]
    },
    "spot": {
        "translation": "地点；斑点",
        "breakdown": [
            {"part": "spot", "origin": "中古英语 spotte", "meaning": "斑点，地点"},
        ]
    },
    "step": {
        "translation": "步骤；台阶",
        "breakdown": [
            {"part": "step", "origin": "古英语 steppa", "meaning": "脚步，步伐"},
        ]
    },
    "stereo": {
        "translation": "立体声；音响",
        "breakdown": [
            {"part": "stereo-", "origin": "希腊语 στερεός", "meaning": "坚固的，立体的"},
        ]
    },
    "story": {
        "translation": "故事",
        "breakdown": [
            {"part": "story", "origin": "古法语 estorie / 拉丁语 historia", "meaning": "历史，叙述"},
        ]
    },
    "string": {
        "translation": "线，弦",
        "breakdown": [
            {"part": "string", "origin": "古英语 streng", "meaning": "绳子，线"},
        ]
    },
    "strip": {
        "translation": "条，带；脱衣",
        "breakdown": [
            {"part": "strip", "origin": "中古英语 stripen", "meaning": "剥去"},
        ]
    },
    "stuff": {
        "translation": "东西，材料",
        "breakdown": [
            {"part": "stuff", "origin": "古法语 estoffe", "meaning": "装备，材料"},
        ]
    },
    "summer": {
        "translation": "夏天",
        "breakdown": [
            {"part": "summer", "origin": "古英语 sumor", "meaning": "夏天"},
        ]
    },
    "survivor": {
        "translation": "幸存者",
        "breakdown": [
            {"part": "sur-", "origin": "拉丁语 super-", "meaning": "超过，之上"},
            {"part": "viv-", "origin": "拉丁语 vivere", "meaning": "活"},
            {"part": "-or", "origin": "施动者后缀", "meaning": "做...的人"},
        ]
    },
    "sweet": {
        "translation": "甜的；亲爱的",
        "breakdown": [
            {"part": "sweet", "origin": "古英语 swēte", "meaning": "甜的"},
        ]
    },
    # T
    "table": {
        "translation": "桌子",
        "breakdown": [
            {"part": "table", "origin": "古法语 table / 拉丁语 tabula", "meaning": "木板，平板"},
        ]
    },
    "theater": {
        "translation": "剧院",
        "breakdown": [
            {"part": "theater", "origin": "拉丁语 theatrum / 希腊语 θέατρον", "meaning": "观看的地方（来自 theasthai 看）"},
        ]
    },
    "thing": {
        "translation": "事物，东西",
        "breakdown": [
            {"part": "thing", "origin": "古英语 þing", "meaning": "集会，事物"},
        ]
    },
    "throat": {
        "translation": "喉咙",
        "breakdown": [
            {"part": "throat", "origin": "古英语 þrotu", "meaning": "喉咙"},
        ]
    },
    "tip": {
        "translation": "尖端；小费",
        "breakdown": [
            {"part": "tip", "origin": "中古英语 tippe", "meaning": "尖端"},
        ]
    },
    "today": {
        "translation": "今天",
        "breakdown": [
            {"part": "to-", "origin": "古英语 tō", "meaning": "在，向"},
            {"part": "day", "origin": "古英语 dæg", "meaning": "天"},
        ]
    },
    "tonight": {
        "translation": "今晚",
        "breakdown": [
            {"part": "to-", "origin": "古英语 tō", "meaning": "在"},
            {"part": "night", "origin": "古英语 niht", "meaning": "夜晚"},
        ]
    },
    "towel": {
        "translation": "毛巾",
        "breakdown": [
            {"part": "towel", "origin": "古法语 toaille", "meaning": "擦布（来自拉丁语 tela 织物）"},
        ]
    },
    "trouble": {
        "translation": "麻烦",
        "breakdown": [
            {"part": "trouble", "origin": "古法语 trouble", "meaning": "混乱（来自拉丁语 turbidus 浑浊的）"},
        ]
    },
    "tuna": {
        "translation": "金枪鱼",
        "breakdown": [
            {"part": "tuna", "origin": "西班牙语 atún / 阿拉伯语 tūn", "meaning": "金枪鱼"},
        ]
    },
    "turtle": {
        "translation": "海龟",
        "breakdown": [
            {"part": "turtle", "origin": "古法语 tortue", "meaning": "弯曲的（来自拉丁语 tortus 扭曲的）"},
        ]
    },
    "tv": {
        "translation": "电视",
        "breakdown": [
            {"part": "tele-", "origin": "希腊语 τῆλε", "meaning": "远的"},
            {"part": "-vision", "origin": "拉丁语 visio", "meaning": "看"},
        ]
    },
    # U
    "universe": {
        "translation": "宇宙",
        "breakdown": [
            {"part": "uni-", "origin": "拉丁语 unus", "meaning": "一"},
            {"part": "-verse", "origin": "拉丁语 versus", "meaning": "转向"},
        ]
    },
    # V
    "vanilla": {
        "translation": "香草",
        "breakdown": [
            {"part": "vanilla", "origin": "西班牙语 vainilla", "meaning": "小豆荚（vaina 豆荚的指小词）"},
        ]
    },
    "vulnerability": {
        "translation": "脆弱性",
        "breakdown": [
            {"part": "vulner-", "origin": "拉丁语 vulnus", "meaning": "伤口"},
            {"part": "-able", "origin": "拉丁语 -abilis", "meaning": "能够...的"},
            {"part": "-ity", "origin": "拉丁语 -itas", "meaning": "名词后缀"},
        ]
    },
    # W
    "watch": {
        "translation": "手表；观看",
        "breakdown": [
            {"part": "watch", "origin": "古英语 wæcce", "meaning": "守夜，警戒"},
        ]
    },
    "way": {
        "translation": "方式；路",
        "breakdown": [
            {"part": "way", "origin": "古英语 weg", "meaning": "路，旅程"},
        ]
    },
    "week": {
        "translation": "周",
        "breakdown": [
            {"part": "week", "origin": "古英语 wice", "meaning": "七天周期"},
        ]
    },
    "whole": {
        "translation": "整体，全部",
        "breakdown": [
            {"part": "whole", "origin": "古英语 hāl", "meaning": "完整的，健康的"},
        ]
    },
    "wine": {
        "translation": "葡萄酒",
        "breakdown": [
            {"part": "wine", "origin": "古英语 wīn / 拉丁语 vinum", "meaning": "葡萄酒"},
        ]
    },
    "witness": {
        "translation": "证人；目击",
        "breakdown": [
            {"part": "wit-", "origin": "古英语 wit", "meaning": "知识，意识"},
            {"part": "-ness", "origin": "古英语 -nes", "meaning": "名词后缀"},
        ]
    },
    "word": {
        "translation": "单词，话",
        "breakdown": [
            {"part": "word", "origin": "古英语 word", "meaning": "词，话语"},
        ]
    },
    "world": {
        "translation": "世界",
        "breakdown": [
            {"part": "wor-", "origin": "古英语 wer", "meaning": "人"},
            {"part": "-ld", "origin": "古英语 -old", "meaning": "年龄，时代"},
        ]
    },
    "worm": {
        "translation": "虫，蠕虫",
        "breakdown": [
            {"part": "worm", "origin": "古英语 wyrm", "meaning": "蛇，虫，龙"},
        ]
    },
    # Y
    "year": {
        "translation": "年",
        "breakdown": [
            {"part": "year", "origin": "古英语 ġēar", "meaning": "年"},
        ]
    },

    # ---- More common words ----
    "abuse": {
        "translation": "虐待，滥用",
        "breakdown": [
            {"part": "ab-", "origin": "拉丁语 ab-", "meaning": "离开，偏离"},
            {"part": "-use", "origin": "拉丁语 uti", "meaning": "使用"},
        ]
    },
    "cafeteria": {
        "translation": "自助餐厅",
        "breakdown": [
            {"part": "cafet-", "origin": "法语 café", "meaning": "咖啡"},
            {"part": "-eria", "origin": "西班牙语 -ería", "meaning": "场所"},
        ]
    },
    "can": {
        "translation": "罐头；能",
        "breakdown": [
            {"part": "can", "origin": "古英语 cann", "meaning": "容器，罐子"},
        ]
    },
    "cookie": {
        "translation": "饼干",
        "breakdown": [
            {"part": "cookie", "origin": "荷兰语 koekje", "meaning": "小蛋糕（koek 蛋糕的指小词）"},
        ]
    },
    "cream": {
        "translation": "奶油",
        "breakdown": [
            {"part": "cream", "origin": "古法语 craime / 拉丁语 chrisma", "meaning": "油膏"},
        ]
    },
    "credit": {
        "translation": "信用；学分",
        "breakdown": [
            {"part": "credit", "origin": "拉丁语 creditum", "meaning": "贷款，信任（来自 credere 相信）"},
        ]
    },
    "crush": {
        "translation": "迷恋；压碎",
        "breakdown": [
            {"part": "crush", "origin": "中古英语 cruschen", "meaning": "压碎"},
        ]
    },
    "cup": {
        "translation": "杯子",
        "breakdown": [
            {"part": "cup", "origin": "古英语 cuppe / 拉丁语 cuppa", "meaning": "杯子"},
        ]
    },
    "cut": {
        "translation": "切，割",
        "breakdown": [
            {"part": "cut", "origin": "中古英语 cutten", "meaning": "切"},
        ]
    },
    "dad": {
        "translation": "爸爸",
        "breakdown": [
            {"part": "dad", "origin": "儿语 dada", "meaning": "爸爸（跨语言通用）"},
        ]
    },
    "daddy": {
        "translation": "爸爸（亲昵）",
        "breakdown": [
            {"part": "dad", "origin": "儿语 dada", "meaning": "爸爸"},
            {"part": "-dy", "origin": "指小后缀", "meaning": "亲昵"},
        ]
    },
    "day": {
        "translation": "天，白天",
        "breakdown": [
            {"part": "day", "origin": "古英语 dæg", "meaning": "白天"},
        ]
    },
    "dear": {
        "translation": "亲爱的",
        "breakdown": [
            {"part": "dear", "origin": "古英语 dēore", "meaning": "珍贵的，亲爱的"},
        ]
    },
    "decision": {
        "translation": "决定",
        "breakdown": [
            {"part": "de-", "origin": "拉丁语 de-", "meaning": "离开"},
            {"part": "-cis-", "origin": "拉丁语 caedere", "meaning": "切"},
            {"part": "-ion", "origin": "名词后缀", "meaning": "表示动作"},
        ]
    },
    "dentist": {
        "translation": "牙医",
        "breakdown": [
            {"part": "dent-", "origin": "拉丁语 dens", "meaning": "牙齿"},
            {"part": "-ist", "origin": "希腊语 -istes", "meaning": "从事...的人"},
        ]
    },
    "diary": {
        "translation": "日记",
        "breakdown": [
            {"part": "diar-", "origin": "拉丁语 diarium", "meaning": "每日的（来自 dies 天）"},
            {"part": "-y", "origin": "名词后缀", "meaning": "表示事物"},
        ]
    },
    "difference": {
        "translation": "差异，不同",
        "breakdown": [
            {"part": "dif-", "origin": "拉丁语 dis-", "meaning": "分开"},
            {"part": "-fer-", "origin": "拉丁语 ferre", "meaning": "携带"},
            {"part": "-ence", "origin": "名词后缀", "meaning": "表示状态"},
        ]
    },
    "dinner": {
        "translation": "晚餐",
        "breakdown": [
            {"part": "dinner", "origin": "古法语 disner", "meaning": "吃早餐（来自拉丁语 disjejunare 打破斋戒）"},
        ]
    },
    "dough": {
        "translation": "面团；钱（俚语）",
        "breakdown": [
            {"part": "dough", "origin": "古英语 dāh", "meaning": "面团"},
        ]
    },
    "dream": {
        "translation": "梦",
        "breakdown": [
            {"part": "dream", "origin": "古英语 drēam", "meaning": "欢乐，音乐"},
        ]
    },
    "dress": {
        "translation": "裙子；穿衣",
        "breakdown": [
            {"part": "dress", "origin": "古法语 dresser", "meaning": "整理，排列（来自拉丁语 directus 直的）"},
        ]
    },
    "end": {
        "translation": "结束；末端",
        "breakdown": [
            {"part": "end", "origin": "古英语 end", "meaning": "末端，结束"},
        ]
    },
    "everybody": {
        "translation": "每个人",
        "breakdown": [
            {"part": "every-", "origin": "古英语 æfre + ælc", "meaning": "每个"},
            {"part": "body", "origin": "古英语 bodig", "meaning": "身体，人"},
        ]
    },
    "everyone": {
        "translation": "每个人",
        "breakdown": [
            {"part": "every-", "origin": "古英语 æfre + ælc", "meaning": "每个"},
            {"part": "one", "origin": "古英语 ān", "meaning": "一"},
        ]
    },
    "factor": {
        "translation": "因素",
        "breakdown": [
            {"part": "fact-", "origin": "拉丁语 facere", "meaning": "做"},
            {"part": "-or", "origin": "施动者后缀", "meaning": "做...的人/物"},
        ]
    },
    "father": {
        "translation": "父亲",
        "breakdown": [
            {"part": "fath-", "origin": "古英语 fæder", "meaning": "父亲"},
            {"part": "-er", "origin": "亲属关系后缀", "meaning": "表示人"},
        ]
    },
    "feeling": {
        "translation": "感觉",
        "breakdown": [
            {"part": "feel", "origin": "古英语 fēlan", "meaning": "触摸，感觉"},
            {"part": "-ing", "origin": "动名词后缀", "meaning": "表示动作/状态"},
        ]
    },
    "flavor": {
        "translation": "味道，风味",
        "breakdown": [
            {"part": "flavor", "origin": "古法语 flaur", "meaning": "气味，味道"},
        ]
    },
    "floor": {
        "translation": "地板；楼层",
        "breakdown": [
            {"part": "floor", "origin": "古英语 flōr", "meaning": "地板，地面"},
        ]
    },
    "freezer": {
        "translation": "冷冻柜",
        "breakdown": [
            {"part": "freez-", "origin": "古英语 frēosan", "meaning": "冻结"},
            {"part": "-er", "origin": "工具后缀", "meaning": "做...的东西"},
        ]
    },
    "fun": {
        "translation": "乐趣",
        "breakdown": [
            {"part": "fun", "origin": "英语方言 funnen", "meaning": "哄骗，戏弄"},
        ]
    },
    "furniture": {
        "translation": "家具",
        "breakdown": [
            {"part": "furnish-", "origin": "古法语 furnir", "meaning": "提供，装备"},
            {"part": "-ure", "origin": "名词后缀", "meaning": "表示结果"},
        ]
    },
    "gesture": {
        "translation": "手势",
        "breakdown": [
            {"part": "gest-", "origin": "拉丁语 gerere", "meaning": "做，执行"},
            {"part": "-ure", "origin": "名词后缀", "meaning": "表示动作"},
        ]
    },
    "god": {
        "translation": "神，上帝",
        "breakdown": [
            {"part": "god", "origin": "古英语 god", "meaning": "神"},
        ]
    },
    "goodnight": {
        "translation": "晚安",
        "breakdown": [
            {"part": "good", "origin": "古英语 gōd", "meaning": "好的"},
            {"part": "night", "origin": "古英语 niht", "meaning": "夜晚"},
        ]
    },
    "gravy": {
        "translation": "肉汁",
        "breakdown": [
            {"part": "gravy", "origin": "古法语 grané", "meaning": "香料调味汁"},
        ]
    },
    "guy": {
        "translation": "家伙，男人",
        "breakdown": [
            {"part": "guy", "origin": "Guy Fawkes（盖伊·福克斯）", "meaning": "指代奇怪的人 → 泛指男人"},
        ]
    },
    "hair": {
        "translation": "头发",
        "breakdown": [
            {"part": "hair", "origin": "古英语 hǣr", "meaning": "头发"},
        ]
    },
    "hairpiece": {
        "translation": "假发片",
        "breakdown": [
            {"part": "hair", "origin": "头发", "meaning": "毛发"},
            {"part": "piece", "origin": "古法语 piece", "meaning": "一块，一片"},
        ]
    },
    "hall": {
        "translation": "大厅，走廊",
        "breakdown": [
            {"part": "hall", "origin": "古英语 heall", "meaning": "大厅，宅邸"},
        ]
    },
    "hammer": {
        "translation": "锤子",
        "breakdown": [
            {"part": "hammer", "origin": "古英语 hamor", "meaning": "锤子"},
        ]
    },
    "hanger": {
        "translation": "衣架；悬挂者",
        "breakdown": [
            {"part": "hang", "origin": "古英语 hon", "meaning": "悬挂"},
            {"part": "-er", "origin": "工具后缀", "meaning": "做...的东西"},
        ]
    },
    "hat": {
        "translation": "帽子",
        "breakdown": [
            {"part": "hat", "origin": "古英语 hætt", "meaning": "帽子"},
        ]
    },
    "head": {
        "translation": "头",
        "breakdown": [
            {"part": "head", "origin": "古英语 hēafod", "meaning": "头，顶部"},
        ]
    },
    "heart": {
        "translation": "心",
        "breakdown": [
            {"part": "heart", "origin": "古英语 heorte", "meaning": "心脏"},
        ]
    },
    "hell": {
        "translation": "地狱",
        "breakdown": [
            {"part": "hell", "origin": "古英语 hel", "meaning": "冥界（来自原始日耳曼语 haljō 隐藏的地方）"},
        ]
    },
    "hero": {
        "translation": "英雄",
        "breakdown": [
            {"part": "hero", "origin": "希腊语 ἥρως (hērōs)", "meaning": "英雄，半神"},
        ]
    },
    "honeymoon": {
        "translation": "蜜月",
        "breakdown": [
            {"part": "honey", "origin": "古英语 hunig", "meaning": "蜂蜜"},
            {"part": "moon", "origin": "古英语 mōna", "meaning": "月亮，月份"},
        ]
    },
    "hour": {
        "translation": "小时",
        "breakdown": [
            {"part": "hour", "origin": "古法语 hore / 拉丁语 hora", "meaning": "小时（来自希腊语 ὥρα）"},
        ]
    },
    "hump": {
        "translation": "驼峰",
        "breakdown": [
            {"part": "hump", "origin": "中古英语 hompe", "meaning": "隆起，驼峰"},
        ]
    },
    "ice": {
        "translation": "冰",
        "breakdown": [
            {"part": "ice", "origin": "古英语 īs", "meaning": "冰"},
        ]
    },
    "jungle": {
        "translation": "丛林",
        "breakdown": [
            {"part": "jungle", "origin": "印地语 jaṅgal", "meaning": "荒地，丛林"},
        ]
    },
    "mom": {
        "translation": "妈妈",
        "breakdown": [
            {"part": "mom", "origin": "儿语 mama", "meaning": "妈妈（跨语言通用）"},
        ]
    },
    "parrot": {
        "translation": "鹦鹉",
        "breakdown": [
            {"part": "parrot", "origin": "法语 perroquet", "meaning": "鹦鹉"},
        ]
    },
    "perform": {
        "translation": "表演",
        "breakdown": [
            {"part": "per-", "origin": "拉丁语 per-", "meaning": "完全"},
            {"part": "-form", "origin": "古法语 former", "meaning": "形成，塑造"},
        ]
    },
    "red": {
        "translation": "红色",
        "breakdown": [
            {"part": "red", "origin": "古英语 rēad", "meaning": "红色"},
        ]
    },
    "reruns": {
        "translation": "重播",
        "breakdown": [
            {"part": "re-", "origin": "拉丁语 re-", "meaning": "再，重新"},
            {"part": "runs", "origin": "古英语 rinnan", "meaning": "跑，播放"},
        ]
    },
    "scream": {
        "translation": "尖叫",
        "breakdown": [
            {"part": "scream", "origin": "中古英语 scremen", "meaning": "尖叫"},
        ]
    },
    "sexually": {
        "translation": "在性方面",
        "breakdown": [
            {"part": "sex", "origin": "拉丁语 sexus", "meaning": "性别"},
            {"part": "-ual", "origin": "拉丁语 -ualis", "meaning": "与...有关的"},
            {"part": "-ly", "origin": "古英语 -līce", "meaning": "副词后缀"},
        ]
    },
    "snap": {
        "translation": "啪；突然折断",
        "breakdown": [
            {"part": "snap", "origin": "拟声词", "meaning": "模拟折断的声音"},
        ]
    },
    "sweetie": {
        "translation": "亲爱的（昵称）",
        "breakdown": [
            {"part": "sweet", "origin": "古英语 swēte", "meaning": "甜的"},
            {"part": "-ie", "origin": "指小后缀", "meaning": "亲昵"},
        ]
    },
    "thank": {
        "translation": "感谢",
        "breakdown": [
            {"part": "thank", "origin": "古英语 þanc", "meaning": "想法，感激"},
        ]
    },
    "whim": {
        "translation": "一时兴起，念头",
        "breakdown": [
            {"part": "whim", "origin": "拟声词 whim-wham", "meaning": "奇想，怪念头"},
        ]
    },
}
