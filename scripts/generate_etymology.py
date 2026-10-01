"""
批量生成西班牙语名词词源学拆分
基于词缀规则和历史词源
"""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_FILE = "src/data/LCDP_S3E01_nouns_cards.json"

# 常见西班牙语词缀及其词源
SUFFIX_PATTERNS = {
    # 名词后缀
    "-ción": {"origin": "拉丁语 -tiōnem", "meaning": "动作/结果名词后缀"},
    "-sión": {"origin": "拉丁语 -siōnem", "meaning": "动作/结果名词后缀"},
    "-dad": {"origin": "拉丁语 -tātem", "meaning": "抽象名词后缀（性质/状态）"},
    "-tad": {"origin": "拉丁语 -tātem", "meaning": "抽象名词后缀"},
    "-ncia": {"origin": "拉丁语 -ntia", "meaning": "抽象名词后缀（状态/性质）"},
    "-ncia": {"origin": "拉丁语 -ntia", "meaning": "抽象名词后缀"},
    "-ero": {"origin": "拉丁语 -ārius", "meaning": "职业/地点/工具后缀"},
    "-era": {"origin": "拉丁语 -āria", "meaning": "阴性职业/地点后缀"},
    "-ista": {"origin": "希腊语 -istēs", "meaning": "从业者/信仰者后缀"},
    "-ismo": {"origin": "希腊语 -ismos", "meaning": "主义/行为/状态后缀"},
    "-ista": {"origin": "希腊语 -istēs", "meaning": "从业者后缀"},
    "-aje": {"origin": "法语 -age / 拉丁语 -aticum", "meaning": "集合/行为后缀"},
    "-anza": {"origin": "拉丁语 -antia", "meaning": "抽象名词后缀"},
    "-encia": {"origin": "拉丁语 -entia", "meaning": "状态/性质后缀"},
    "-ura": {"origin": "拉丁语 -ūra", "meaning": "结果/状态后缀"},
    "-miento": {"origin": "拉丁语 -mentum", "meaning": "行为/结果后缀"},
    "-mento": {"origin": "拉丁语 -mentum", "meaning": "行为/结果后缀"},
    "-dor": {"origin": "拉丁语 -tōrem", "meaning": "行为者/工具后缀"},
    "-dora": {"origin": "拉丁语 -tōra", "meaning": "阴性行为者后缀"},
    "-nte": {"origin": "拉丁语 -ntem", "meaning": "现在分词/行为者后缀"},
    "-ante": {"origin": "拉丁语 -antem", "meaning": "行为者后缀"},
    "-iente": {"origin": "拉丁语 -ientem", "meaning": "行为者后缀"},
    "-or": {"origin": "拉丁语 -ōrem", "meaning": "行为者/工具后缀"},
    "-ora": {"origin": "拉丁语 -ōra", "meaning": "阴性行为者后缀"},
    "-aje": {"origin": "法语 -age", "meaning": "行为/集合后缀"},
    
    # 指小后缀
    "-ito": {"origin": "指小后缀", "meaning": "小/亲昵"},
    "-ita": {"origin": "指小后缀", "meaning": "小/亲昵（阴性）"},
    "-illo": {"origin": "指小后缀", "meaning": "小/轻微"},
    "-illa": {"origin": "指小后缀", "meaning": "小/轻微（阴性）"},
    "-ico": {"origin": "指小后缀", "meaning": "小"},
    "-ica": {"origin": "指小后缀", "meaning": "小（阴性）"},
    "-uelo": {"origin": "指小后缀", "meaning": "小/轻微"},
    "-uela": {"origin": "指小后缀", "meaning": "小/轻微（阴性）"},
    
    # 指大后缀
    "-ón": {"origin": "指大后缀", "meaning": "大/增强"},
    "-ona": {"origin": "指大后缀", "meaning": "大/增强（阴性）"},
    "-azo": {"origin": "指大后缀/打击后缀", "meaning": "大/猛烈打击"},
    "-aza": {"origin": "指大后缀", "meaning": "大（阴性）"},
    
    # 其他后缀
    "-al": {"origin": "拉丁语 -ālem", "meaning": "相关/属于"},
    "-ar": {"origin": "拉丁语 -ārem", "meaning": "相关/属于"},
    "-ario": {"origin": "拉丁语 -ārium", "meaning": "相关/场所"},
    "-aria": {"origin": "拉丁语 -āria", "meaning": "相关/场所（阴性）"},
    "-oso": {"origin": "拉丁语 -ōsus", "meaning": "充满...的"},
    "-osa": {"origin": "拉丁语 -ōsa", "meaning": "充满...的（阴性）"},
    "-ible": {"origin": "拉丁语 -ibilis", "meaning": "能够...的"},
    "-able": {"origin": "拉丁语 -abilis", "meaning": "能够...的"},
    "-ivo": {"origin": "拉丁语 -īvus", "meaning": "相关/倾向"},
    "-iva": {"origin": "拉丁语 -īva", "meaning": "相关/倾向（阴性）"},
    
    # 性别标记
    "-o": {"origin": "阳性名词后缀", "meaning": "名词标记"},
    "-a": {"origin": "阴性名词后缀", "meaning": "名词标记"},
    "-e": {"origin": "名词后缀", "meaning": "名词标记"},
    "-s": {"origin": "复数标记", "meaning": "西班牙语复数后缀"},
}

# 常见词根词源
ROOT_ETYMOLOGY = {
    # A
    "andr-": {"origin": "希腊语 anēr/andros", "meaning": "男人"},
    "balc-": {"origin": "拉丁语 Balkanēs", "meaning": "巴尔干（地名）"},
    "barr-": {"origin": "拉丁语 barra", "meaning": "条/杆 → 街区"},
    "bol-": {"origin": "拉丁语 bulla", "meaning": "气泡/球 → 傻瓜"},
    "bomb-": {"origin": "拟声词 bomba", "meaning": "爆炸声"},
    "brag-": {"origin": "拉丁语 braca", "meaning": "裤子"},
    "busc-": {"origin": "拉丁语 buscare", "meaning": "寻找"},
    "callej-": {"origin": "拉丁语 callis", "meaning": "小路"},
    "camin-": {"origin": "拉丁语 caminus", "meaning": "路"},
    "can-": {"origin": "拉丁语 canalis", "meaning": "管道/渠道"},
    "cant-": {"origin": "拉丁语 cantus", "meaning": "歌唱"},
    "capac-": {"origin": "拉丁语 capax", "meaning": "能够容纳的"},
    "capill-": {"origin": "拉丁语 capella", "meaning": "小教堂（capa 斗篷的指小）"},
    "carg-": {"origin": "拉丁语 carricare", "meaning": "装载"},
    "carib-": {"origin": "加勒比语 Caribe", "meaning": "加勒比（地名/族名）"},
    "cariñ-": {"origin": "拉丁语 carus", "meaning": "亲爱的"},
    "cas-": {"origin": "拉丁语 casa", "meaning": "房子"},
    "celd-": {"origin": "拉丁语 cella", "meaning": "小房间/细胞"},
    "centr-": {"origin": "希腊语 kentron", "meaning": "中心"},
    "cert-": {"origin": "拉丁语 certus", "meaning": "确定的"},
    "champ-": {"origin": "法语 champagne", "meaning": "香槟（地名）"},
    "cit-": {"origin": "拉丁语 citare", "meaning": "召唤/引用"},
    "clas-": {"origin": "拉丁语 classis", "meaning": "阶级/类别"},
    "comand-": {"origin": "拉丁语 commandare", "meaning": "委托/命令"},
    "comid-": {"origin": "拉丁语 comedere", "meaning": "吃"},
    "comunic-": {"origin": "拉丁语 communicare", "meaning": "分享/交流"},
    "contig-": {"origin": "拉丁语 contingere", "meaning": "接触"},
    "continent-": {"origin": "拉丁语 continens", "meaning": "包含的"},
    "control-": {"origin": "拉丁语 contrarotulus", "meaning": "对照记录"},
    "corr-": {"origin": "拉丁语 currere", "meaning": "跑"},
    "corredor-": {"origin": "拉丁语 currere", "meaning": "跑 → 走廊"},
    "crimin-": {"origin": "拉丁语 crimen", "meaning": "罪行"},
    "cri-": {"origin": "拉丁语 criare", "meaning": "创造/抚养"},
    "cul-": {"origin": "拉丁语 culus", "meaning": "臀部"},
    "culp-": {"origin": "拉丁语 culpa", "meaning": "过错"},
    "decis-": {"origin": "拉丁语 decidere", "meaning": "决定（de- + caedere 切）"},
    "declar-": {"origin": "拉丁语 declarare", "meaning": "声明（de- + clarus 清楚）"},
    
    # 更多词根...
}

def find_suffix(word):
    """查找单词的后缀"""
    word_lower = word.lower()
    # 按长度排序，优先匹配长后缀
    sorted_suffixes = sorted(SUFFIX_PATTERNS.keys(), key=len, reverse=True)
    for suffix in sorted_suffixes:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            return suffix
    return None

def generate_etymology(word):
    """为单词生成词源学拆分"""
    word_lower = word.lower()
    
    # 检查是否是专有名词（首字母大写且不在句首）
    if word[0].isupper() and len(word) > 1:
        return None  # 专有名词跳过
    
    # 查找后缀
    suffix = find_suffix(word_lower)
    
    if suffix:
        stem = word_lower[:-len(suffix)]
        # 查找词根词源
        root_info = ROOT_ETYMOLOGY.get(stem + "-", None)
        if not root_info:
            # 尝试更短的词根
            for root_key in ROOT_ETYMOLOGY:
                if stem.startswith(root_key[:-1]):  # 去掉末尾的-
                    root_info = ROOT_ETYMOLOGY[root_key]
                    break
        
        if root_info:
            return [
                {"part": stem + "-", "origin": root_info["origin"], "meaning": root_info["meaning"]},
                {"part": suffix, "origin": SUFFIX_PATTERNS[suffix]["origin"], "meaning": SUFFIX_PATTERNS[suffix]["meaning"]}
            ]
        else:
            # 只有后缀信息
            return [
                {"part": stem + "-", "origin": "西班牙语词根", "meaning": "词干"},
                {"part": suffix, "origin": SUFFIX_PATTERNS[suffix]["origin"], "meaning": SUFFIX_PATTERNS[suffix]["meaning"]}
            ]
    
    # 简单单词，尝试直接匹配词根
    for root_key, root_info in ROOT_ETYMOLOGY.items():
        if word_lower.startswith(root_key[:-1]):
            # 查找剩余部分
            remaining = word_lower[len(root_key[:-1]):]
            if remaining:
                suffix_info = SUFFIX_PATTERNS.get(remaining, None)
                if suffix_info:
                    return [
                        {"part": root_key[:-1] + "-", "origin": root_info["origin"], "meaning": root_info["meaning"]},
                        {"part": remaining, "origin": suffix_info["origin"], "meaning": suffix_info["meaning"]}
                    ]
            else:
                return [
                    {"part": word_lower, "origin": root_info["origin"], "meaning": root_info["meaning"]}
                ]
    
    return None

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        cards = json.load(f)
    
    updated = 0
    skipped = 0
    no_etym = 0
    
    for card in cards:
        if card.get("etymology") and len(card["etymology"]) > 0:
            continue  # 已有词源学
        
        word = card["target_word"]
        etym = generate_etymology(word)
        
        if etym:
            card["etymology"] = etym
            updated += 1
        elif word[0].isupper():
            skipped += 1  # 专有名词
        else:
            no_etym += 1
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"Updated: {updated}")
    print(f"Skipped (proper nouns): {skipped}")
    print(f"No etymology generated: {no_etym}")

if __name__ == "__main__":
    main()
