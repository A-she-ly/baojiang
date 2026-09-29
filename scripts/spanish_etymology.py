"""
Spanish Noun Etymology Dictionary
==================================
Common etymology patterns for Spanish nouns.

Format: {noun_lower: {"translation": "中文", "breakdown": [{"part": "...", "origin": "...", "meaning": "..."}]}}
"""

ETYMOLOGY_DICT = {
    # ---- A ----
    "abrazo": {
        "translation": "拥抱",
        "breakdown": [
            {"part": "abraza-", "origin": "拉丁语 abbrachiāre", "meaning": "拥抱（ab- + bracchium 手臂）"},
            {"part": "-o", "origin": "西班牙语阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "abuela": {
        "translation": "祖母，外婆",
        "breakdown": [
            {"part": "abu-", "origin": "拉丁语 avia", "meaning": "祖母"},
            {"part": "-ela", "origin": "指小后缀", "meaning": "亲昵/ diminutive"},
        ]
    },
    "acento": {
        "translation": "口音，重音",
        "breakdown": [
            {"part": "acen-", "origin": "拉丁语 accentus", "meaning": "音调（ad- + cantus 歌唱）"},
            {"part": "-to", "origin": "过去分词后缀", "meaning": "名词化"},
        ]
    },
    "agua": {
        "translation": "水",
        "breakdown": [
            {"part": "agu-", "origin": "拉丁语 aqua", "meaning": "水"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "agujero": {
        "translation": "洞，孔",
        "breakdown": [
            {"part": "aguj-", "origin": "拉丁语 acūcula", "meaning": "针（acus 针的指小形式）"},
            {"part": "-ero", "origin": "地点/工具后缀", "meaning": "与...相关的地方"},
        ]
    },
    "aire": {
        "translation": "空气，风",
        "breakdown": [
            {"part": "air-", "origin": "拉丁语 aer / aërem", "meaning": "空气（借自希腊语 ἀήρ）"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "aires": {
        "translation": "空气（复数），风气",
        "breakdown": [
            {"part": "aire", "origin": "拉丁语 aer", "meaning": "空气"},
            {"part": "-s", "origin": "复数标记", "meaning": "西班牙语复数后缀"},
        ]
    },
    "ala": {
        "translation": "翅膀",
        "breakdown": [
            {"part": "al-", "origin": "拉丁语 ala", "meaning": "翅膀"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "altura": {
        "translation": "高度",
        "breakdown": [
            {"part": "alt-", "origin": "拉丁语 altus", "meaning": "高的"},
            {"part": "-ura", "origin": "抽象名词后缀", "meaning": "表示性质/状态"},
        ]
    },
    "amanecer": {
        "translation": "黎明，日出",
        "breakdown": [
            {"part": "amanec-", "origin": "拉丁语 ad + mane", "meaning": "到早晨（manē 早晨）"},
            {"part": "-er", "origin": "动词不定式后缀", "meaning": "也可作名词"},
        ]
    },
    "amante": {
        "translation": "情人，爱人",
        "breakdown": [
            {"part": "am-", "origin": "拉丁语 amāre", "meaning": "爱"},
            {"part": "-ante", "origin": "现在分词后缀", "meaning": "正在...的人"},
        ]
    },
    "amigo": {
        "translation": "朋友",
        "breakdown": [
            {"part": "amig-", "origin": "拉丁语 amīcus", "meaning": "朋友（来自 amāre 爱）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "amor": {
        "translation": "爱",
        "breakdown": [
            {"part": "am-", "origin": "拉丁语 amor", "meaning": "爱（来自动词 amāre）"},
            {"part": "-or", "origin": "抽象名词后缀", "meaning": "表示情感/状态"},
        ]
    },
    "arma": {
        "translation": "武器",
        "breakdown": [
            {"part": "arm-", "origin": "拉丁语 arma", "meaning": "武器，装备"},
            {"part": "-a", "origin": "阴性名词后缀（但常以复数 armas 使用）", "meaning": "名词标记"},
        ]
    },
    "arte": {
        "translation": "艺术",
        "breakdown": [
            {"part": "art-", "origin": "拉丁语 ars / artem", "meaning": "技艺，技能"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "asia": {
        "translation": "亚洲",
        "breakdown": [
            {"part": "Asi-", "origin": "古希腊语 σία", "meaning": "东方之地"},
            {"part": "-a", "origin": "地名后缀", "meaning": "大陆名"},
        ]
    },
    "atajo": {
        "translation": "捷径",
        "breakdown": [
            {"part": "ataj-", "origin": "阿拉伯语 at-taqṭīʿ", "meaning": "切割，截断"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "atasco": {
        "translation": "堵塞，交通拥堵",
        "breakdown": [
            {"part": "atasc-", "origin": "可能来自巴斯克语或前罗马语", "meaning": "塞住"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "austeridad": {
        "translation": " austerity, 简朴",
        "breakdown": [
            {"part": "auster-", "origin": "拉丁语 austerus", "meaning": "严厉的，简朴的"},
            {"part": "-idad", "origin": "抽象名词后缀（对应英语 -ity）", "meaning": "表示性质"},
        ]
    },
    "autobús": {
        "translation": "公共汽车",
        "breakdown": [
            {"part": "auto-", "origin": "希腊语 αὐτός", "meaning": "自己，自动"},
            {"part": "bús", "origin": "omnibus 的缩写", "meaning": "为所有人（拉丁语 omnibus）"},
        ]
    },
    "aventura": {
        "translation": "冒险",
        "breakdown": [
            {"part": "aventur-", "origin": "拉丁语 adventūra", "meaning": "即将发生的事（advenīre 到来）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "avión": {
        "translation": "飞机",
        "breakdown": [
            {"part": "avi-", "origin": "拉丁语 avis", "meaning": "鸟"},
            {"part": "-ón", "origin": "增大后缀", "meaning": "大的/增强"},
        ]
    },
    "ayuda": {
        "translation": "帮助",
        "breakdown": [
            {"part": "ayud-", "origin": "拉丁语 adiūtāre", "meaning": "帮助（adiuvāre 的反复形式）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "azotea": {
        "translation": "屋顶平台",
        "breakdown": [
            {"part": "azot-", "origin": "阿拉伯语 aṣ-ṣuṭayḥa", "meaning": "小平台"},
            {"part": "-ea", "origin": "地点后缀", "meaning": "表示地方"},
        ]
    },
    "año": {
        "translation": "年",
        "breakdown": [
            {"part": "añ-", "origin": "拉丁语 annus", "meaning": "年"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- B ----
    "banco": {
        "translation": "银行；长凳",
        "breakdown": [
            {"part": "banc-", "origin": "日耳曼语 *bank", "meaning": "长凳（早期货币兑换商坐的长凳）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "banda": {
        "translation": "乐队；帮派",
        "breakdown": [
            {"part": "band-", "origin": "日耳曼语 *banda", "meaning": "带子，群体"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "barco": {
        "translation": "船",
        "breakdown": [
            {"part": "barc-", "origin": "拉丁语 barca", "meaning": "小船（来自凯尔特语）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "basura": {
        "translation": "垃圾",
        "breakdown": [
            {"part": "basur-", "origin": "可能来自巴斯克语 bazterra", "meaning": "边缘，废料"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "bañera": {
        "translation": "浴缸",
        "breakdown": [
            {"part": "bañ-", "origin": "拉丁语 balneum", "meaning": "洗澡"},
            {"part": "-era", "origin": "容器/地点后缀", "meaning": "用于...的容器"},
        ]
    },
    "baño": {
        "translation": "浴室；洗澡",
        "breakdown": [
            {"part": "bañ-", "origin": "拉丁语 balneum", "meaning": "浴场"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "brazo": {
        "translation": "手臂",
        "breakdown": [
            {"part": "braz-", "origin": "拉丁语 brachium", "meaning": "手臂（来自希腊语 βραχίων）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- C ----
    "cabeza": {
        "translation": "头",
        "breakdown": [
            {"part": "cabez-", "origin": "拉丁语 capitia", "meaning": "头（caput 头的衍生）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "calle": {
        "translation": "街道",
        "breakdown": [
            {"part": "call-", "origin": "拉丁语 callis", "meaning": "小路，路径"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "calor": {
        "translation": "热",
        "breakdown": [
            {"part": "cal-", "origin": "拉丁语 calor", "meaning": "热（来自 calēre 发热）"},
            {"part": "-or", "origin": "抽象名词后缀", "meaning": "表示性质/状态"},
        ]
    },
    "camino": {
        "translation": "路，道路",
        "breakdown": [
            {"part": "camin-", "origin": "拉丁语 caminus", "meaning": "炉灶，路径"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "campo": {
        "translation": "田野，场地",
        "breakdown": [
            {"part": "camp-", "origin": "拉丁语 campus", "meaning": "平原，田野"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "cara": {
        "translation": "脸",
        "breakdown": [
            {"part": "car-", "origin": "拉丁语 cara", "meaning": "脸（来自希腊语 κάρα 头）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "casa": {
        "translation": "房子",
        "breakdown": [
            {"part": "cas-", "origin": "拉丁语 casa", "meaning": "小屋，茅舍"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "cielo": {
        "translation": "天空",
        "breakdown": [
            {"part": "ciel-", "origin": "拉丁语 caelum", "meaning": "天空，天堂"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "ciudad": {
        "translation": "城市",
        "breakdown": [
            {"part": "ciud-", "origin": "拉丁语 civitas", "meaning": "公民身份，城市"},
            {"part": "-ad", "origin": "抽象名词后缀（来自 -tatem）", "meaning": "表示状态/集体"},
        ]
    },
    "coche": {
        "translation": "汽车",
        "breakdown": [
            {"part": "coch-", "origin": "匈牙利语 kocsi", "meaning": "来自 Kocs 村的马车"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "corazón": {
        "translation": "心脏",
        "breakdown": [
            {"part": "corazon-", "origin": "拉丁语 cor / cordis", "meaning": "心"},
            {"part": "-ón", "origin": "增大后缀", "meaning": "强调/增大"},
        ]
    },
    "cosa": {
        "translation": "东西，事物",
        "breakdown": [
            {"part": "cos-", "origin": "拉丁语 causa", "meaning": "原因，事物"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "cuerpo": {
        "translation": "身体",
        "breakdown": [
            {"part": "cuerp-", "origin": "拉丁语 corpus", "meaning": "身体"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- D ----
    "día": {
        "translation": "天，日子",
        "breakdown": [
            {"part": "dí-", "origin": "拉丁语 dies", "meaning": "天"},
            {"part": "-a", "origin": "特殊：拉丁语 dies 是阳性但以 -a 结尾", "meaning": "名词标记"},
        ]
    },
    "dinero": {
        "translation": "钱",
        "breakdown": [
            {"part": "diner-", "origin": "拉丁语 denarius", "meaning": "第纳尔银币"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "dios": {
        "translation": "神",
        "breakdown": [
            {"part": "di-", "origin": "拉丁语 deus", "meaning": "神"},
            {"part": "-os", "origin": "复数形式保留", "meaning": "单数也保留 -os 结尾"},
        ]
    },
    "dolor": {
        "translation": "疼痛",
        "breakdown": [
            {"part": "dol-", "origin": "拉丁语 dolor", "meaning": "痛苦（来自 dolēre 疼痛）"},
            {"part": "-or", "origin": "抽象名词后缀", "meaning": "表示情感/状态"},
        ]
    },
    
    # ---- E ----
    "escuela": {
        "translation": "学校",
        "breakdown": [
            {"part": "escuel-", "origin": "拉丁语 schola", "meaning": "闲暇，学习场所（来自希腊语 σχολή）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "espacio": {
        "translation": "空间",
        "breakdown": [
            {"part": "espaci-", "origin": "拉丁语 spatium", "meaning": "距离，空间"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "esperanza": {
        "translation": "希望",
        "breakdown": [
            {"part": "esperanz-", "origin": "拉丁语 sperantia", "meaning": "希望（sperāre 希望）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "estrella": {
        "translation": "星星",
        "breakdown": [
            {"part": "estrell-", "origin": "拉丁语 stella", "meaning": "星"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- F ----
    "familia": {
        "translation": "家庭",
        "breakdown": [
            {"part": "famili-", "origin": "拉丁语 familia", "meaning": "家庭，仆人"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "flor": {
        "translation": "花",
        "breakdown": [
            {"part": "fl-", "origin": "拉丁语 flos / floris", "meaning": "花"},
            {"part": "-or", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "fuego": {
        "translation": "火",
        "breakdown": [
            {"part": "fueg-", "origin": "拉丁语 focus", "meaning": "壁炉，火"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- G ----
    "gente": {
        "translation": "人，人们",
        "breakdown": [
            {"part": "gent-", "origin": "拉丁语 gens / gentis", "meaning": "种族，人民"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "guerra": {
        "translation": "战争",
        "breakdown": [
            {"part": "guerr-", "origin": "日耳曼语 *werra", "meaning": "争执，混乱"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- H ----
    "hijo": {
        "translation": "儿子",
        "breakdown": [
            {"part": "hij-", "origin": "拉丁语 filius", "meaning": "儿子（f→h 音变）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "historia": {
        "translation": "历史，故事",
        "breakdown": [
            {"part": "histori-", "origin": "拉丁语 historia", "meaning": "调查，叙述（来自希腊语 ἱστορία）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "hombre": {
        "translation": "男人",
        "breakdown": [
            {"part": "hombr-", "origin": "拉丁语 homo / hominis", "meaning": "人"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "hora": {
        "translation": "小时",
        "breakdown": [
            {"part": "hor-", "origin": "拉丁语 hora", "meaning": "小时（来自希腊语 ὥρα）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- L ----
    "luz": {
        "translation": "光",
        "breakdown": [
            {"part": "luz", "origin": "拉丁语 lux / lucis", "meaning": "光"},
        ]
    },
    
    # ---- M ----
    "madre": {
        "translation": "母亲",
        "breakdown": [
            {"part": "madr-", "origin": "拉丁语 mater", "meaning": "母亲"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "mano": {
        "translation": "手",
        "breakdown": [
            {"part": "man-", "origin": "拉丁语 manus", "meaning": "手"},
            {"part": "-o", "origin": "特殊：拉丁语 manus 是阴性但以 -o 结尾", "meaning": "名词标记"},
        ]
    },
    "mar": {
        "translation": "海",
        "breakdown": [
            {"part": "mar", "origin": "拉丁语 mare", "meaning": "海"},
        ]
    },
    "mes": {
        "translation": "月，月份",
        "breakdown": [
            {"part": "mes", "origin": "拉丁语 mensis", "meaning": "月"},
        ]
    },
    "mundo": {
        "translation": "世界",
        "breakdown": [
            {"part": "mund-", "origin": "拉丁语 mundus", "meaning": "世界，宇宙"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "muerte": {
        "translation": "死亡",
        "breakdown": [
            {"part": "muert-", "origin": "拉丁语 mors / mortis", "meaning": "死亡"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- N ----
    "nombre": {
        "translation": "名字",
        "breakdown": [
            {"part": "nombr-", "origin": "拉丁语 nomen", "meaning": "名字"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "noche": {
        "translation": "夜晚",
        "breakdown": [
            {"part": "noch-", "origin": "拉丁语 nox / noctis", "meaning": "夜"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- O ----
    "ojo": {
        "translation": "眼睛",
        "breakdown": [
            {"part": "oj-", "origin": "拉丁语 oculus", "meaning": "眼睛"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "oro": {
        "translation": "金",
        "breakdown": [
            {"part": "or-", "origin": "拉丁语 aurum", "meaning": "金（au→o 音变）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- P ----
    "padre": {
        "translation": "父亲",
        "breakdown": [
            {"part": "padr-", "origin": "拉丁语 pater", "meaning": "父亲"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "palabra": {
        "translation": "词，话",
        "breakdown": [
            {"part": "palabr-", "origin": "拉丁语 parabola", "meaning": "比喻，话语（来自希腊语 παραβολή）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "pan": {
        "translation": "面包",
        "breakdown": [
            {"part": "pan", "origin": "拉丁语 panis", "meaning": "面包"},
        ]
    },
    "parte": {
        "translation": "部分",
        "breakdown": [
            {"part": "part-", "origin": "拉丁语 pars / partis", "meaning": "部分"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "paz": {
        "translation": "和平",
        "breakdown": [
            {"part": "paz", "origin": "拉丁语 pax / pacis", "meaning": "和平"},
        ]
    },
    "pez": {
        "translation": "鱼",
        "breakdown": [
            {"part": "pez", "origin": "拉丁语 piscis", "meaning": "鱼（pis→pe 音变）"},
        ]
    },
    "pie": {
        "translation": "脚",
        "breakdown": [
            {"part": "pi-", "origin": "拉丁语 pes / pedis", "meaning": "脚"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
    "puerta": {
        "translation": "门",
        "breakdown": [
            {"part": "puert-", "origin": "拉丁语 porta", "meaning": "门"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- R ----
    "rey": {
        "translation": "国王",
        "breakdown": [
            {"part": "rey", "origin": "拉丁语 rex / regis", "meaning": "国王（reg→rey 音变）"},
        ]
    },
    "río": {
        "translation": "河",
        "breakdown": [
            {"part": "rí-", "origin": "拉丁语 rivus", "meaning": "小溪，河"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "rosa": {
        "translation": "玫瑰",
        "breakdown": [
            {"part": "ros-", "origin": "拉丁语 rosa", "meaning": "玫瑰"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- S ----
    "sol": {
        "translation": "太阳",
        "breakdown": [
            {"part": "sol", "origin": "拉丁语 sol", "meaning": "太阳"},
        ]
    },
    "sombra": {
        "translation": "影子",
        "breakdown": [
            {"part": "sombr-", "origin": "拉丁语 umbra", "meaning": "阴影（umb→sombr 增音）"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- T ----
    "tiempo": {
        "translation": "时间",
        "breakdown": [
            {"part": "tiemp-", "origin": "拉丁语 tempus", "meaning": "时间"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "tierra": {
        "translation": "土地，地球",
        "breakdown": [
            {"part": "tierr-", "origin": "拉丁语 terra", "meaning": "土地"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    
    # ---- V ----
    "vida": {
        "translation": "生命",
        "breakdown": [
            {"part": "vid-", "origin": "拉丁语 vita", "meaning": "生命"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "viento": {
        "translation": "风",
        "breakdown": [
            {"part": "vient-", "origin": "拉丁语 ventus", "meaning": "风"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "voz": {
        "translation": "声音",
        "breakdown": [
            {"part": "voz", "origin": "拉丁语 vox / vocis", "meaning": "声音"},
        ]
    },
    
    # ---- 其他常见词 ----
    "libro": {
        "translation": "书",
        "breakdown": [
            {"part": "libr-", "origin": "拉丁语 liber", "meaning": "书（原意树皮）"},
            {"part": "-o", "origin": "阳性名词后缀", "meaning": "名词标记"},
        ]
    },
    "mesa": {
        "translation": "桌子",
        "breakdown": [
            {"part": "mes-", "origin": "拉丁语 mensa", "meaning": "桌子"},
            {"part": "-a", "origin": "阴性名词后缀", "meaning": "名词标记"},
        ]
    },
    "noche": {
        "translation": "夜晚",
        "breakdown": [
            {"part": "noch-", "origin": "拉丁语 nox / noctis", "meaning": "夜"},
            {"part": "-e", "origin": "名词后缀", "meaning": "名词标记"},
        ]
    },
}
