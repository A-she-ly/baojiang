"""
Script: parse_lcdp_s01e01.py
Purpose:
  1. Parse the Money Heist (La Casa de Papel) S01E01 Spanish subtitle file.
  2. Build structured JSON: metadata.json, cards.json.
  3. Flashcards designed for Chinese learners of Spanish.

Run:
  python scripts/parse_lcdp_s01e01.py
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


# ---------------------------------------------------------------------------
# SRT Parser
# ---------------------------------------------------------------------------
def parse_srt(path: Path) -> List[Dict[str, Any]]:
    """Parse an SRT subtitle file into a list of subtitle entries."""
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\s*\n", text.strip())
    entries = []
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        # First line: sequence number
        seq = lines[0].strip()
        if not seq.isdigit():
            continue
        # Second line: timestamp
        ts_match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not ts_match:
            continue
        start, end = ts_match.group(1), ts_match.group(2)
        # Remaining lines: text
        subtitle_text = " ".join(lines[2:]).strip()
        if subtitle_text:
            entries.append({
                "seq": int(seq),
                "start": start,
                "end": end,
                "text": subtitle_text,
            })
    return entries


# ---------------------------------------------------------------------------
# Scene detection (based on time gaps)
# ---------------------------------------------------------------------------
def detect_scenes(entries: List[Dict], gap_threshold_sec: float = 10.0) -> List[Dict[str, Any]]:
    """Split subtitles into scenes based on time gaps."""
    def ts_to_sec(ts: str) -> float:
        h, m, rest = ts.split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    scenes: List[Dict[str, Any]] = []
    current_scene_lines: List[Dict] = []
    scene_start = 0.0
    prev_end = 0.0

    for entry in entries:
        start_sec = ts_to_sec(entry["start"])
        end_sec = ts_to_sec(entry["end"])

        if current_scene_lines and (start_sec - prev_end) > gap_threshold_sec:
            # New scene
            scenes.append({
                "scene_id": f"scene_{len(scenes)+1:03d}",
                "start": current_scene_lines[0]["start"],
                "end": current_scene_lines[-1]["end"],
                "lines": current_scene_lines,
            })
            current_scene_lines = []

        current_scene_lines.append(entry)
        prev_end = end_sec

    if current_scene_lines:
        scenes.append({
            "scene_id": f"scene_{len(scenes)+1:03d}",
            "start": current_scene_lines[0]["start"],
            "end": current_scene_lines[-1]["end"],
            "lines": current_scene_lines,
        })

    return scenes


# ---------------------------------------------------------------------------
# Character detection (simple heuristic)
# ---------------------------------------------------------------------------
# Known characters from Money Heist S01E01
KNOWN_CHARACTERS = {
    "Tokio": ["tokio"],
    "El Profesor": ["profesor", "professor"],
    "Berlín": ["berlin", "berlín"],
    "Moscú": ["moscu", "moscú"],
    "Denver": ["denver"],
    "Río": ["rio", "río"],
    "Nairobi": ["nairobi"],
    "Helsinki": ["helsinki"],
    "Oslo": ["oslo"],
    "Arturo Román": ["arturo", "roman"],
    "Raquel Murillo": ["raquel", "murillo", "inspectora"],
    "Ángel Rubio": ["angel", "rubio"],
    "Alison Parker": ["alison", "parker"],
    "Mónica Gaztambre": ["monica", "gaztambre"],
    "Mercedes": ["mercedes"],
    "Su madre": ["mamá", "madre", "mama"],
}


def detect_character(text: str) -> str:
    """Simple character detection based on keywords."""
    text_lower = text.lower()
    for char_name, keywords in KNOWN_CHARACTERS.items():
        for kw in keywords:
            if kw in text_lower:
                return char_name
    return "Narrador"  # Default to narrator (Tokio narrates)


# ---------------------------------------------------------------------------
# Curated flashcards for La Casa de Papel S01E01
# Designed for Chinese learners of Spanish
# ---------------------------------------------------------------------------
def build_cards(scenes: List[Dict[str, Any]], entries: List[Dict]) -> List[Dict[str, Any]]:
    """
    Build curated flashcards.
    Each card: target_word, ipa (Spanish IPA), pos, level, pronunciation_focus,
    tags, sentence_cloze, sentence_full, translation (Chinese),
    sentence_translation (Chinese), cultural_note (Chinese), scene_id, character
    """

    # Helper: find the scene_id and character for a given subtitle text
    def find_context(search_text: str) -> Tuple[str, str, str]:
        """Returns (scene_id, character, full_text)"""
        search_lower = search_text.lower()
        for scene in scenes:
            for line in scene["lines"]:
                if search_lower in line["text"].lower():
                    char = detect_character(line["text"])
                    return scene["scene_id"], char, line["text"]
        return scenes[0]["scene_id"], "Narrador", search_text

    # Spanish pronunciation focus categories
    # rolled_r: rolled/trilled R (rr, r at start)
    # tapped_r: tapped R (single r between vowels)
    # ny_sound: ñ sound /ɲ/
    # ll_y: ll/y distinction or yeísmo
    # vowel_a: Spanish /a/
    # vowel_e: Spanish /e/
    # vowel_i: Spanish /i/
    # vowel_o: Spanish /o/
    # vowel_u: Spanish /u/
    # diphthong: Spanish diphthongs (ie, ue, ui, etc.)
    # silent_h: silent H
    # c_z_distinction: c/z pronunciation (Spain: /θ/ vs Latin America: /s/)
    # j_sound: j/g before e,i = /x/
    # gl_gu: g pronunciation (/g/ vs /ɣ/ vs silent)

    cards_raw = [
        # ---- Opening / Tokio's narration ----

        # 1. "detente" - imperative, very common
        ("detente", "/deˈtente/", "v. (imperativo) 停下，站住", "A2", "tapped_r",
         ["imperativo", "高频动词", "A2"],
         "¡___ o dispararé!",
         "¡Detente o dispararé!",
         "站住，不然我开枪了！",
         "detenerse 的反身动词命令式。detente = 你停下。西班牙警察剧高频词。",
         "scene_001", "¡Detente o dispararé!"),

        # 2. "dispararé" - future tense
        ("dispararé", "/dispaˈaɾe/", "v. (futuro) 我将开枪", "B1", "tapped_r",
         ["futuro", "高频动词", "B1"],
         "¡Detente o ___!",
         "¡Detente o dispararé!",
         "站住，不然我开枪了！",
         "disparar = 开枪、射击。-é 结尾是第一人称将来时：我将...。西语将来时变位规则。",
         "scene_001", "¡Detente o dispararé!"),

        # 3. "mi nombre es" - 基础句型
        ("nombre", "/ˈnom.bɾe/", "n.m. 名字，名称", "A1", "vowel_o",
         ["A1基础", "高频名词"],
         "Mi ___ es Tokio.",
         "Mi nombre es Tokio.",
         "我的名字叫东京。",
         "nombre = 名字。Mi nombre es... = 我叫...（最基础的自我介绍句型）。注意 mb 连读。",
         "scene_001", "Mi nombre es Tokio."),

        # 4. "cuando comenzó" - 简单过去时
        ("comenzó", "/komenˈso/", "v. (pretérito) 开始了", "A2", "vowel_o",
         ["pretérito", "高频动词", "A2"],
         "Pero cuando ___ esta historia...",
         "Pero cuando comenzó esta historia...",
         "但当这个故事开始的时候……",
         "comenzar = 开始。comenzó 是简单过去时第三人称。注意 z→c 的变位：comencé, comenzó。",
         "scene_001", "Pero cuando comenzó esta historia"),

        # 5. "el amor de mi vida" - 经典表达
        ("amor de mi vida", "/aˈmoɾ e mi ˈbiða/", "n. phrase 我生命中的爱", "A2", "vowel_a",
         ["经典表达", "情感", "A2"],
         "Y esto, el ___ ___ ___ ___ ___ ___.",
         "Y esto, el amor de mi vida.",
         "而这个，是我一生的挚爱。",
         "el amor de mi vida = 我生命中的爱人。西语非常浪漫高频的表达。注意 de 弱读为 /ðe/。",
         "scene_001", "el amor de mi vida"),

        # 6. "robo" - 核心词汇
        ("robo", "/ˈro.βo/", "n.m. 抢劫，盗窃", "B1", "rolled_r",
         ["核心词汇", "B1", "剧情关键词"],
         "El ___ se quita el tiro.",
         "El robo se quita el tiro.",
         "抢劫中擦枪走火了。",
         "robo = 抢劫/盗窃。本剧核心词。注意 r 在词首发颤音 /r/，b 在元音间发 /β/。",
         "scene_001", "El robo se quita el tiro"),

        # 7. "charco de sangre" - 生动表达
        ("charco", "/ˈtʃa.ko/", "n.m. 水坑，血泊", "B1", "tapped_r",
         ["生动表达", "B1"],
         "Lo dejé en un ___ de sangre.",
         "Lo dejé en un charco de sangre.",
         "我让他倒在了一滩血泊之中。",
         "charco = 水坑。charco de sangre = 血泊。ch 发 /t/，和英语 church 的 ch 一样。",
         "scene_001", "charco de sangre"),

        # 8. "sangre" - 高频词
        ("sangre", "/ˈsaŋ.ɡɾe/", "n.f. 血", "B1", "rolled_r",
         ["高频名词", "B1"],
         "Lo dejé en un charco de ___.",
         "Lo dejé en un charco de sangre.",
         "我让他倒在了一滩血泊之中。",
         "sangre = 血。注意 ng 发 /ŋ/（和英语 sing 一样），gre 中 r 发颤音。",
         "scene_001", "charco de sangre"),

        # 9. "robos limpios" - 形容词后置
        ("limpio", "/ˈlim.pjo/", "adj. 干净的，利落的", "B1", "vowel_i",
         ["形容词", "B1"],
         "Hicimos 15 ___ ___...",
         "Hicimos 15 robos limpios...",
         "我们干了15票干净的活儿……",
         "limpio = 干净的。西语形容词放在名词后面：robos limpios（干净的抢劫）。注意 mp 连读。",
         "scene_001", "robos limpios"),

        # 10. "mezclando" - 副动词
        ("mezclando", "/mesˈklan.do/", "v. (gerundio) 混合，掺杂", "B1", "vowel_e",
         ["gerundio", "B1", "高频动词"],
         "pero ___ amor y trabajo nunca funciona.",
         "pero mezclando amor y trabajo nunca funciona.",
         "但把爱情和工作混在一起从来都行不通。",
         "mezclar = 混合。mezclando 是副动词（-ando 形式），表示正在进行的动作。",
         "scene_001", "mezclando amor y trabajo"),

        # 11. "funciona" - 超高频动词
        ("funciona", "/fuŋˈsjo.na/", "v. 运作，行得通", "A2", "diphthong",
         ["A2高频", "超常用动词"],
         "mezclando amor y trabajo nunca ___.",
         "mezclando amor y trabajo nunca funciona.",
         "把爱情和工作混在一起从来都行不通。",
         "funcionar = 运作、行得通。no funciona = 不管用/行不通。西语日常超高频词。",
         "scene_001", "nunca funciona"),

        # 12. "guardia de seguridad" - 复合名词
        ("guardia", "/ˈɡwaɾ.ðja/", "n.m./f. 警卫，守卫", "B1", "diphthong",
         ["复合名词", "B1", "职业"],
         "Entonces, cuando el ___ de seguridad disparó...",
         "Entonces, cuando el guardia de seguridad disparó...",
         "所以当那个保安开枪的时候……",
         "guardia = 警卫/警察。注意 gu 发 /ɡw/，ia 是双元音 /ja/。guardia de seguridad = 保安。",
         "scene_001", "guardia de seguridad"),

        # 13. "ladrón" - 重音在最后一个音节
        ("ladrón", "/laˈðɾon/", "n.m. 小偷，盗贼", "B1", "tapped_r",
         ["B1核心", "职业"],
         "Del ___ al asesino.",
         "Del ladrón al asesino.",
         "从小偷变成了杀人犯。",
         "ladrón = 小偷。重音在最后一个音节（-ón），所以有重音符号。注意 dr 连读。",
         "scene_001", "Del ladrón al asesino"),

        # 14. "asesino" - 核心词
        ("asesino", "/aˈse.si.no/", "n.m. 杀手，凶手", "B1", "vowel_e",
         ["B1核心", "剧情关键词"],
         "Del ladrón al ___.",
         "Del ladrón al asesino.",
         "从小偷变成了杀人犯。",
         "asesino = 杀手/凶手。asesinar = 谋杀。注意 s 在元音间发 /s/（拉美）或 /θ/（西班牙）。",
         "scene_001", "Del ladrón al asesino"),

        # 15. "huir" - 不规则动词
        ("huir", "/wiɾ/", "v. 逃跑，逃离", "B1", "diphthong",
         ["不规则动词", "B1", "高频"],
         "Y así es como empecé a ___.",
         "Y así es como empecé a huir.",
         "我就这样开始了逃亡之路。",
         "huir = 逃跑。h 不发音！uir 发 /wiɾ/。不规则变位：huyo, huyes, huye...",
         "scene_001", "empecé a huir"),

        # 16. "escondido" - 过去分词作形容词
        ("escondido", "/es.konˈði.ðo/", "adj. 藏起来的，躲藏的", "B1", "vowel_i",
         ["过去分词", "B1"],
         "Llevo 11 días ___.",
         "Llevo 11 días escondido.",
         "我已经躲了11天了。",
         "esconder = 藏。escondido 是过去分词，这里当形容词用。注意 d 在元音间发 /ð/。",
         "scene_001", "Llevo 11 días escondido"),

        # 17. "empapelada" - 生动用词
        ("empapelada", "/em.pa.peˈla.ða/", "adj. (被)贴满（通缉令）的", "C1", "vowel_a",
         ["生动用词", "C1"],
         "y mi foto ___ en estaciones de policía...",
         "y mi foto empapelada en estaciones de policía...",
         "我的照片被贴满了全西班牙的警察局。",
         "empapelar = 贴纸/贴满。empapelada = 被贴满（通缉令）。非常生动的西语表达。",
         "scene_001", "mi foto empapelada"),

        # 18. "sentencia" - 法律词汇
        ("sentencia", "/senˈten.θja/", "n.f. 判决，刑期", "B2", "c_z_distinction",
         ["法律词汇", "B2", "CET6对应"],
         "Obtendría una ___ de 30 años.",
         "Obtendría una sentencia de 30 años.",
         "我会被判30年有期徒刑。",
         "sentencia = 判决/刑期。注意 c 在 e/i 前在西班牙发 /θ/（类似英语 th），拉美发 /s/。",
         "scene_001", "sentencia de 30 años"),

        # 19. "envejecer" - 动词
        ("envejecer", "/em.be.xeˈθeɾ/", "v. 变老，衰老", "B1", "j_sound",
         ["B1动词", "身体"],
         "a quien le gusta ___.",
         "a quien le gusta envejecer.",
         "喜欢变老的人。",
         "envejecer = 变老。注意 j 发 /x/（类似汉语 h 但更重）。c 在 e 前西班牙发 /θ/。",
         "scene_001", "gusta envejecer"),

        # 20. "celda" - 监狱词汇
        ("celda", "/ˈθel.ða/", "n.f. 牢房，囚室", "B2", "c_z_distinction",
         ["监狱词汇", "B2"],
         "En la ___ de una prisión.",
         "En la celda de una prisión.",
         "在监狱的牢房里。",
         "celda = 牢房。c 在 e 前西班牙发 /θ/，d 在元音间发 /ð/。prisión = 监狱。",
         "scene_001", "celda de una prisión"),

        # ---- Scene: Meeting the Professor ----

        # 21. "ángel de la guarda" - 文化表达
        ("ángel de la guarda", "/ˈaŋ.xel ðe la ˈɡwaɾ.ða/", "n. phrase 守护天使", "B1", "j_sound",
         ["文化表达", "B1", "宗教"],
         "Apareció mi ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___.",
         "Apareció mi ángel de la guarda.",
         "我的守护天使出现了。",
         "ángel de la guarda = 守护天使。天主教文化中西班牙人常用表达。注意 ng 发 //。",
         "scene_002", "ángel de la guarda"),

        # 22. "a ciencia cierta" - 固定搭配
        ("a ciencia cierta", "/a ˈθjen.θja ˈθjeɾ.ta/", "phrase 确切地，肯定地", "C1", "c_z_distinction",
         ["固定搭配", "C1", "高级表达"],
         "Pero nunca se sabe ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___",
         "Pero nunca se sabe a ciencia cierta.",
         "但你永远无法确切知道。",
         "a ciencia cierta = 确切地/肯定地。高级固定搭配，西语母语者常用。ciencia = 科学/知识。",
         "scene_002", "a ciencia cierta"),

        # 23. "disculpe" - 礼貌用语
        ("disculpe", "/disˈkul.pe/", "v. (formal) 请问，劳驾，对不起", "A2", "vowel_u",
         ["礼貌用语", "A2", "超高频"],
         "___, ¿tiene un minuto?",
         "Disculpe, ¿tiene un minuto?",
         "打扰一下，您有一分钟吗？",
         "disculpe = 打扰了/请问（正式）。日常超高频礼貌用语。discúlpeme = 请原谅我。",
         "scene_002", "Disculpe, ¿tiene un minuto?"),

        # 24. "matadero" - 特定场所词
        ("matadero", "/ma.taˈðe.ɾo/", "n.m. 屠宰场", "B2", "tapped_r",
         ["特定场所", "B2"],
         "Iba al ___.",
         "Iba al matadero.",
         "我正要去屠宰场。",
         "matar = 杀 → matadero = 屠宰场。-dero 是表示场所的后缀。注意 d 发 /ð/。",
         "scene_002", "iba al matadero"),

        # 25. "negocios" - 商业词汇
        ("negocios", "/neˈɡo.sjos/", "n.m.pl. 生意，交易", "A2", "diphthong",
         ["商业词汇", "A2", "高频"],
         "Quiero proponer algunos ___.",
         "Quiero proponer algunos negocios.",
         "我想谈一笔生意。",
         "negocio = 生意/买卖。proponer negocios = 提出交易。注意 ci 发 /θj/（西班牙）或 /sj/（拉美）。",
         "scene_002", "proponer algunos negocios"),

        # 26. "singular" - 形容词
        ("singular", "/siŋ.ɡuˈlaɾ/", "adj. 独特的，非凡的", "B1", "rolled_r",
         ["B1形容词", "高级表达"],
         "un robo que es ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___......",
         "un robo que es singular.",
         "一次独一无二的抢劫。",
         "singular = 独特的/非凡的。也可以指语法中的「单数」。注意 gu 发 /ɡw/。",
         "scene_002", "un robo que es singular"),

        # 27. "perder" - 核心动词
        ("perder", "/peɾðeɾ/", "v. 失去，损失", "A2", "tapped_r",
         ["A2核心动词", "高频"],
         "gente que no tienen mucho que ___.",
         "gente que no tienen mucho que perder.",
         "那些没什么可失去的人。",
         "perder = 失去/输掉。不规则变位：pierdo, pierdes... 注意 d 在元音间发 /ð/。",
         "scene_002", "mucho que perder"),

        # ---- Scene: The heist begins ----

        # 28. "Fábrica de Moneda y Timbre" - 专有名词
        ("fábrica", "/ˈfa.bɾi.ka/", "n.f. 工厂，制造厂", "B1", "tapped_r",
         ["专有名词", "B1", "地点"],
         "En la ___ de Moneda y Timbre.",
         "En la Fábrica de Moneda y Timbre.",
         "在皇家铸币造印厂。",
         "fábrica = 工厂。重音在第一个音节。Fábrica de Moneda y Timbre = 西班牙皇家铸币局（真实地点）。",
         "scene_003", "Fábrica de Moneda y Timbre"),

        # 29. "apoyo urgente" - 紧急呼叫
        ("urgente", "/uɾˈxen.te/", "adj. 紧急的", "B1", "j_sound",
         ["紧急用语", "B1"],
         "Apoyo ___.",
         "Apoyo urgente.",
         "请求紧急支援。",
         "urgente = 紧急的。g 在 e/i 前发 /x/（类似汉语 h）。apoyo = 支援/支持。",
         "scene_003", "Apoyo urgente"),

        # 30. "velocidad del sonido" - 物理术语
        ("velocidad", "/be.lo.θiˈðað/", "n.f. 速度", "B1", "c_z_distinction",
         ["物理术语", "B1", "CET4对应"],
         "Vuela más rápido que la ___ del sonido.",
         "Vuela más rápido que la velocidad del sonido.",
         "它飞得比音速还快。",
         "velocidad = 速度。v 在西语发 /b/（不是英语的 v）。注意 c 在 i 前西班牙发 /θ/。",
         "scene_003", "velocidad del sonido"),

        # 31. "corazón" - 情感核心词
        ("corazón", "/ko.ɾaˈθon/", "n.m. 心脏，心", "A2", "c_z_distinction",
         ["A2核心", "身体", "情感"],
         "si te disparan en el ___.",
         "si te disparan en el corazón.",
         "如果朝你的心脏开一枪……",
         "corazón = 心脏/心。重音在最后一个音节所以有重音符。z 在词尾西班牙发 /θ/。",
         "scene_003", "en el corazón"),

        # 32. "bala" - 武器词汇
        ("bala", "/ˈba.la/", "n.f. 子弹", "B1", "vowel_a",
         ["武器词汇", "B1"],
         "Se dispara una ___ M16...",
         "Se dispara una bala M16...",
         "一发M16子弹射出……",
         "bala = 子弹。简单但重要的词。注意两个 a 都发 /a/，西语的 a 比汉语的 a 更靠后。",
         "scene_003", "una bala M16"),

        # 33. "milisegundo" - 时间单位
        ("milisegundo", "/mi.li.seˈɡun.do/", "n.m. 毫秒", "B2", "vowel_u",
         ["时间单位", "B2"],
         "en un ___.",
         "en un milisegundo.",
         "在一毫秒之内。",
         "milli-（千分之一）+ segundo（秒）= milisegundo。segundo 注意 g 发 /ɡ/。",
         "scene_003", "en un milisegundo"),

        # 34. "costumbre" - 习惯
        ("costumbre", "/kosˈtum.bɾe/", "n.f. 习惯，惯例", "B1", "vowel_u",
         ["B1名词", "高频"],
         "Y de la misma manera que de ___.",
         "Y de la misma manera que de costumbre.",
         "就像往常一样。",
         "costumbre = 习惯/惯例。de costumbre = 通常/照例。注意 mb 连读 /mbɾe/。",
         "scene_003", "que de costumbre"),

        # ---- Additional high-value cards ----

        # 35. "mierda" - 高频粗口（了解即可）
        ("mierda", "/ˈmjeɾ.ða/", "interj./n.f. 该死，狗屎", "B1", "diphthong",
         ["口语粗口", "B1", "了解即可"],
         "¡___!",
         "¡Mierda!",
         "该死！",
         "mierda = 屎/该死。西语最高频粗口之一。ie 是双元音 /je/。了解即可，不必主动使用。",
         "scene_003", "¡Mierda!"),

        # 36. "oficial caído" - 警察术语
        ("caído", "/kaˈi.ðo/", "adj. 倒下的，阵亡的", "B1", "diphthong",
         ["警察术语", "B1"],
         "Oficial ___.",
         "Oficial caído.",
         "有警员倒下/阵亡。",
         "caer = 倒下/掉落。caído 是过去分词作形容词。注意 í 是重读的 i，和 o 不构成双元音。",
         "scene_003", "Oficial caído"),

        # 37. "repito" - 通讯用语
        ("repito", "/reˈpi.to/", "v. 我重复", "A2", "vowel_i",
         ["通讯用语", "A2"],
         "___, oficial abajo.",
         "Repito, oficial abajo.",
         "重复一遍，有警员倒地。",
         "repetir = 重复。repito = 我重复（第一人称现在时）。无线电通讯高频词。",
         "scene_003", "Repito, oficial abajo"),

        # 38. "escucharás" - 将来时
        ("escucharás", "/es.ku.tʃaˈɾas/", "v. (futuro) 你将听到", "A2", "tapped_r",
         ["futuro", "A2", "感官动词"],
         "ni siquiera ___ la bala que te ha matado.",
         "ni siquiera escucharás la bala que te ha matado.",
         "你甚至听不到杀死你的那颗子弹的声音。",
         "escuchar = 听。escucharás = 你将听到（第二人称将来时）。siquiera = 甚至。",
         "scene_003", "escucharás la bala"),

        # 39. "joder" - 超高频口语（了解）
        ("jodidamente", "/xo.di.ðaˈmen.te/", "adv. 他妈地，极其", "B2", "j_sound",
         ["口语强化词", "B2", "了解即可"],
         "Esto no podría haber comenzado ___ peor.",
         "Esto no podría haber comenzado jodidamente peor.",
         "这开局简直不能再他妈糟了！",
         "joder 的词根 + -mente 副词后缀。极度口语化强化词。了解含义即可。",
         "scene_003", "jodidamente peor"),

        # 40. "santa mierda" - 感叹语
        ("santa", "/ˈsan.ta/", "adj. 神圣的（感叹用）", "B1", "vowel_a",
         ["感叹语", "B1"],
         "¡___ mierda!",
         "¡Santa mierda!",
         "我的天啊！",
         "santa = 神圣的。santa mierda = 我的天/我靠（类似 holy shit）。sant 发 /san/。",
         "scene_003", "¡Santa mierda!"),
    ]

    cards = []
    for i, (target_word, ipa, pos, level, pronunciation_focus, tags,
            sentence_cloze, sentence_full, translation,
            cultural_note, scene_kw, search_text) in enumerate(cards_raw, start=1):

        scene_id, character, _ = find_context(search_text)

        cards.append({
            "id": f"LCDP_S01E01_{i:03d}",
            "episode": "S01E01",
            "scene_id": scene_id,
            "line_index": i,
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
            "sentence_translation": translation,
            "cultural_note": cultural_note,
            "screenshot": f"/episodes/LCDP_S01E01/images/{scene_id}.png",
            "frequency_rank": None,
            "is_example_sentence": False,
        })

    return cards


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    root = Path(__file__).resolve().parent.parent
    srt_path = root / "es" / "Money.Heist.S01E01.SPANiSH.WEBRip.x264-ION10-es.srt"
    out_dir = root / "public" / "episodes" / "LCDP_S01E01"
    src_data_dir = root / "src" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    src_data_dir.mkdir(parents=True, exist_ok=True)

    if not srt_path.exists():
        print(f"ERROR: SRT not found: {srt_path}", file=sys.stderr)
        return 1

    entries = parse_srt(srt_path)
    scenes = detect_scenes(entries)
    cards = build_cards(scenes, entries)

    metadata = {
        "episode": "S01E01",
        "title": "Efecto Mariposa",
        "title_cn": "蝴蝶效应",
        "description": "La primera episodio — Tokio narra cómo conoció al Profesor y comenzó el mayor robo de la historia en la Fábrica Nacional de Moneda y Timbre.",
        "scenes_count": len(scenes),
        "dialogue_lines_count": len(entries),
        "characters": sorted(set(KNOWN_CHARACTERS.keys()) | {"Narrador"}),
        "scenes_summary": [
            {
                "scene_id": s["scene_id"],
                "scene_name": f"Escena {i+1} ({s['start']} - {s['end']})",
                "lines_count": len(s["lines"]),
            }
            for i, s in enumerate(scenes)
        ],
    }

    # Write JSON
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (src_data_dir / "LCDP_S01E01_cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (src_data_dir / "LCDP_S01E01_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] metadata.json -> {len(metadata['characters'])} characters, {metadata['scenes_count']} scenes")
    print(f"[OK] cards.json    -> {len(cards)} flashcards")
    print(f"   output: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
