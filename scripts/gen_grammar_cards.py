import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

cards = [
    # Card 1: 主格人称代词
    {
        "id": "GRAMMAR_subject_pronouns",
        "episode": "",
        "scene_id": "",
        "line_index": 0,
        "character": "",
        "target_word": "\u6ca1\u6709\u5b58\u5728\u611f\u7684\u4f60\u6211\u4ed6",
        "ipa": "",
        "pos": "grammar",
        "level": "A1",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u4ee3\u8bcd", "\u4e3b\u683c\u4eba\u79f0\u4ee3\u8bcd"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "\u4e3b\u683c\u4eba\u79f0\u4ee3\u8bcd\uff1ayo, t\u00fa, \u00e9l/ella, nosotros, vosotros, ellos",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "\u4e3b\u683c\u4eba\u79f0\u4ee3\u8bcd",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u8bf7\u586b\u5199\u6bcf\u4e2a\u897f\u73ed\u7259\u8bed\u4eba\u79f0\u4ee3\u8bcd\u5bf9\u5e94\u7684\u4e2d\u6587\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u5355\u6570</th><th>\u590d\u6570</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>\u7b2c\u4e00\u4eba\u79f0</b></td>'
            '<td><b>yo</b> <input type="text" class="grammar-input" data-answer="\u6211" placeholder="\u4e2d\u6587..."/></td>'
            '<td><b>nosotros / nosotras</b> <input type="text" class="grammar-input" data-answer="\u6211\u4eec" placeholder="\u4e2d\u6587..."/></td>'
            '</tr>'
            '<tr><td><b>\u7b2c\u4e8c\u4eba\u79f0\uff08\u975e\u6b63\u5f0f\uff09</b></td>'
            '<td><b>t\u00fa</b> <input type="text" class="grammar-input" data-answer="\u4f60" placeholder="\u4e2d\u6587..."/></td>'
            '<td><b>vosotros / vosotras</b> <input type="text" class="grammar-input" data-answer="\u4f60\u4eec" placeholder="\u4e2d\u6587..."/></td>'
            '</tr>'
            '<tr><td><b>\u7b2c\u4e8c\u4eba\u79f0\uff08\u6b63\u5f0f\uff09</b></td>'
            '<td><b>usted</b> <input type="text" class="grammar-input" data-answer="\u60a8" placeholder="\u4e2d\u6587..."/></td>'
            '<td><b>ustedes</b> <input type="text" class="grammar-input" data-answer="\u60a8\u4eec/\u4f60\u4eec" placeholder="\u4e2d\u6587..."/></td>'
            '</tr>'
            '<tr><td><b>\u7b2c\u4e09\u4eba\u79f0</b></td>'
            '<td><b>\u00e9l / ella</b> <input type="text" class="grammar-input" data-answer="\u4ed6/\u5979" placeholder="\u4e2d\u6587..."/></td>'
            '<td><b>ellos / ellas</b> <input type="text" class="grammar-input" data-answer="\u4ed6\u4eec/\u5979\u4eec" placeholder="\u4e2d\u6587..."/></td>'
            '</tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<p class="grammar-intro">\u897f\u73ed\u7259\u8bed\u7684<b>\u4e3b\u683c\u4eba\u79f0\u4ee3\u8bcd</b>'
            '（\u4e5f\u5c31\u662f\u201c\u6211\u3001\u4f60\u3001\u4ed6\u3001\u6211\u4eec\u3001\u4f60\u4eec\u3001\u4ed6\u4eec\u201d）\u975e\u5e38\u597d\u7406\u89e3\u3002</p>'
            '<p class="grammar-summary">\u7528\u4e00\u53e5\u8bdd\u603b\u7ed3\uff1a\u5b83\u4eec\u5c31\u662f\u52a8\u4f5c\u7684<b>\u201c\u53d1\u8d77\u8005\u201d</b>\uff0c'
            '\u4f46\u5728\u897f\u8bed\u91cc\uff0c\u5b83\u4eec\u975e\u5e38<b>\u201c\u6ca1\u5b58\u5728\u611f\u201d</b>\uff0c\u7ecf\u5e38\u88ab\u7701\u7565\u3002</p>'
            '<p class="grammar-desc">\u4e0b\u9762\u7ed9\u4f60\u901a\u4fd7\u5730\u62c6\u89e3\u4e00\u4e0b\uff1a</p>'
            '<h3>\u6838\u5fc3\u8868\u683c\uff08\u8c01\u5728\u505a\u4e8b\uff1f\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u5355\u6570</th><th>\u590d\u6570</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>\u7b2c\u4e00\u4eba\u79f0</b></td><td><b>yo</b> (\u6211)</td><td><b>nosotros / nosotras</b> (\u6211\u4eec)</td></tr>'
            '<tr><td><b>\u7b2c\u4e8c\u4eba\u79f0\uff08\u975e\u6b63\u5f0f\uff09</b></td><td><b>t\u00fa</b> (\u4f60)</td><td><b>vosotros / vosotras</b> (\u4f60\u4eec) <i>\u3010\u4ec5\u9650\u897f\u73ed\u7259\u3011</i></td></tr>'
            '<tr><td><b>\u7b2c\u4e8c\u4eba\u79f0\uff08\u6b63\u5f0f\uff09</b></td><td><b>usted</b> (\u60a8)</td><td><b>ustedes</b> (\u60a8\u4eec / \u4f60\u4eec) <i>\u3010\u62c9\u7f8e\u901a\u7528\u3011</i></td></tr>'
            '<tr><td><b>\u7b2c\u4e09\u4eba\u79f0</b></td><td><b>\u00e9l</b> (\u4ed6) / <b>ella</b> (\u5979)</td><td><b>ellos</b> (\u4ed6\u4eec) / <b>ellas</b> (\u5979\u4eec)</td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\U0001f4a1 \u5173\u952e\u8bb0\u5fc6\u70b9\uff1a</b>'
            '<ul>'
            '<li>\u897f\u8bed\u52a8\u8bcd\u53d8\u4f4d\u5df2\u7ecf\u5305\u542b\u4e86\u4eba\u79f0\u4fe1\u606f\uff0c\u6240\u4ee5\u4ee3\u8bcd\u7ecf\u5e38<b>\u7701\u7565</b>\u3002\u4f8b\u5982\uff1a<code>Hablo espa\u00f1ol</code> = \u6211\u8bf4\u897f\u8bed\uff08\u4e0d\u9700\u8981\u8bf4 Yo\uff09</li>'
            '<li><b>nosotros</b>\uff08\u5168\u7537\u6216\u6df7\u5408\uff09vs <b>nosotras</b>\uff08\u5168\u5973\uff09\u2014\u2014\u897f\u8bed\u6709\u9634\u9633\u6027\u4e4b\u5206</li>'
            '<li><b>vosotros</b> \u53ea\u5728\u897f\u73ed\u7259\u7528\uff0c\u62c9\u7f8e\u7528 <b>ustedes</b> \u4ee3\u66ff</li>'
            '<li><b>usted / ustedes</b> \u662f\u6b63\u5f0f\u79f0\u547c\uff0c\u52a8\u8bcd\u7528\u7b2c\u4e09\u4eba\u79f0\u53d8\u4f4d</li>'
            '</ul></div></div>'
        )
    },
    # Card 2: ser 陈述式现在时
    {
        "id": "GRAMMAR_ser_presente",
        "episode": "",
        "scene_id": "",
        "line_index": 1,
        "character": "",
        "target_word": "ser \u00b7 \u9648\u8ff0\u5f0f\u73b0\u5728\u65f6",
        "ipa": "",
        "pos": "grammar",
        "level": "A1",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u73b0\u5728\u65f6"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u9648\u8ff0\u5f0f\u73b0\u5728\u65f6\u53d8\u4f4d\uff1asoy, eres, es, somos, sois, son",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u9648\u8ff0\u5f0f\u73b0\u5728\u65f6",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u9648\u8ff0\u5f0f\u73b0\u5728\u65f6\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th><th>\u4e2d\u6587</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>yo</b></td><td><input type="text" class="grammar-input" data-answer="soy" placeholder="..."/></td><td>\u6211\u662f</td></tr>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="eres" placeholder="..."/></td><td>\u4f60\u662f</td></tr>'
            '<tr><td><b>\u00e9l/ella/usted</b></td><td><input type="text" class="grammar-input" data-answer="es" placeholder="..."/></td><td>\u4ed6/\u5979/\u60a8\u662f</td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="somos" placeholder="..."/></td><td>\u6211\u4eec\u662f</td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="sois" placeholder="..."/></td><td>\u4f60\u4eec\u662f</td></tr>'
            '<tr><td><b>ellos/ellas/ustedes</b></td><td><input type="text" class="grammar-input" data-answer="son" placeholder="..."/></td><td>\u4ed6\u4eec/\u5979\u4eec/\u60a8\u4eec\u662f</td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<p class="grammar-intro"><b>ser</b>\uff08\u662f\uff09\u548c <b>estar</b>\uff08\u5904\u4e8e\uff09\u5e76\u5217\u4e3a\u897f\u73ed\u7259\u8bed\u6700\u57fa\u7840\u3001<b>\u4e5f\u6700\u4e0d\u89c4\u5219</b>\u7684\u4e24\u4e2a\u52a8\u8bcd\u3002</p>'
            '<p class="grammar-summary">ser \u7684\u53d8\u4f4d\u4e4b\u6240\u4ee5\u91cd\u8981\uff0c\u662f\u56e0\u4e3a\u5b83<b>\u592a\u5e38\u7528</b>\uff0c\u800c\u4e14\u6781\u5ea6\u4e0d\u89c4\u5219\uff0c\u51e0\u4e4e\u5168\u9760\u6b7b\u8bb0\u786c\u80cc\uff0c\u4f46\u597d\u5728\u6bcf\u4e2a\u65f6\u6001\u7684\u89c4\u5f8b\u90fd\u6bd4\u8f83\u56fa\u5b9a\u3002</p>'
            '<h3>1. \u9648\u8ff0\u5f0f\u73b0\u5728\u65f6\uff08\u6700\u5e38\u7528\uff0c\u5fc5\u987b\u79d2\u61c2\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th><th>\u4e2d\u6587</th></tr></thead>'
            '<tbody>'
            '<tr><td>yo</td><td><b>soy</b></td><td>\u6211\u662f</td></tr>'
            '<tr><td>t\u00fa</td><td><b>eres</b></td><td>\u4f60\u662f</td></tr>'
            '<tr><td>\u00e9l/ella/usted</td><td><b>es</b></td><td>\u4ed6/\u5979/\u60a8\u662f</td></tr>'
            '<tr><td>nosotros/as</td><td><b>somos</b></td><td>\u6211\u4eec\u662f</td></tr>'
            '<tr><td>vosotros/as</td><td><b>sois</b></td><td>\u4f60\u4eec\u662f (\u4ec5\u897f\u73ed\u7259)</td></tr>'
            '<tr><td>ellos/ellas/ustedes</td><td><b>son</b></td><td>\u4ed6\u4eec/\u5979\u4eec/\u60a8\u4eec\u662f</td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\U0001f4a1 \u5f00\u53d1\u8005\u63d0\u793a\uff1a</b>'
            '<ul>'
            '<li>\u6ce8\u610f <code>es</code>\u3002\u5728\u73b0\u5728\u65f6\u91cc\uff0c<code>yo</code> \u7684\u5f62\u5f0f\u662f <code>soy</code>\uff0c\u975e\u5e38\u7279\u6b8a</li>'
            '<li><code>vosotros</code> \u662f <code>sois</code>\uff0c\u4e5f\u662f\u552f\u4e00\u5e26 <code>-is</code> \u7ed3\u5c3e\u7684</li>'
            '</ul></div></div>'
        )
    },
    # Card 3: ser 简单过去时
    {
        "id": "GRAMMAR_ser_pretérito",
        "episode": "",
        "scene_id": "",
        "line_index": 2,
        "character": "",
        "target_word": "ser \u00b7 \u7b80\u5355\u8fc7\u53bb\u65f6",
        "ipa": "",
        "pos": "grammar",
        "level": "A2",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u8fc7\u53bb\u65f6"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u7b80\u5355\u8fc7\u53bb\u65f6\u53d8\u4f4d\uff1afui, fuiste, fue, fuimos, fuisteis, fueron",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u7b80\u5355\u8fc7\u53bb\u65f6",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u7b80\u5355\u8fc7\u53bb\u65f6\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>yo</b></td><td><input type="text" class="grammar-input" data-answer="fui" placeholder="..."/></td></tr>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="fuiste" placeholder="..."/></td></tr>'
            '<tr><td><b>\u00e9l/ella/usted</b></td><td><input type="text" class="grammar-input" data-answer="fue" placeholder="..."/></td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="fuimos" placeholder="..."/></td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="fuisteis" placeholder="..."/></td></tr>'
            '<tr><td><b>ellos/ellas/ustedes</b></td><td><input type="text" class="grammar-input" data-answer="fueron" placeholder="..."/></td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<h3>2. \u7b80\u5355\u8fc7\u53bb\u65f6\uff08\u8bb2\u6545\u4e8b\u3001\u53d9\u8ff0\u8fc7\u53bb\u53d1\u751f\u7684\u4e8b\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td>yo</td><td><b>fui</b></td></tr>'
            '<tr><td>t\u00fa</td><td><b>fuiste</b></td></tr>'
            '<tr><td>\u00e9l/ella/usted</td><td><b>fue</b></td></tr>'
            '<tr><td>nosotros/as</td><td><b>fuimos</b></td></tr>'
            '<tr><td>vosotros/as</td><td><b>fuisteis</b></td></tr>'
            '<tr><td>ellos/ellas/ustedes</td><td><b>fueron</b></td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\u26a0\ufe0f \u5de8\u5927\u5751\u70b9\uff1a</b>'
            '<ul>'
            '<li>ser \u7684\u7b80\u5355\u8fc7\u53bb\u65f6\u548c\u52a8\u8bcd <b>ir</b>\uff08\u53bb\uff09\u7684\u7b80\u5355\u8fc7\u53bb\u65f6<b>\u4e00\u6a21\u4e00\u6837</b>\uff01</li>'
            '<li>\u6bd4\u5982 <code>Fui a Madrid</code> \u53ef\u4ee5\u662f\u201c\u6211\u53bb\u4e86\u9a6c\u5fb7\u91cc\u201d(ir)\uff0c\u4e5f\u53ef\u4ee5\u662f\u201c\u6211\u66fe\u5728\u9a6c\u5fb7\u91cc\u201d(ser)\u3002<b>\u53ea\u80fd\u9760\u4e0a\u4e0b\u6587\u5224\u65ad</b>\u3002</li>'
            '</ul></div></div>'
        )
    },
    # Card 4: ser 未完成过去时
    {
        "id": "GRAMMAR_ser_imperfecto",
        "episode": "",
        "scene_id": "",
        "line_index": 3,
        "character": "",
        "target_word": "ser \u00b7 \u672a\u5b8c\u6210\u8fc7\u53bb\u65f6",
        "ipa": "",
        "pos": "grammar",
        "level": "A2",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u8fc7\u53bb\u65f6"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u672a\u5b8c\u6210\u8fc7\u53bb\u65f6\u53d8\u4f4d\uff1aera, eras, era, \u00e9ramos, erais, eran",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u672a\u5b8c\u6210\u8fc7\u53bb\u65f6",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u672a\u5b8c\u6210\u8fc7\u53bb\u65f6\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>yo</b></td><td><input type="text" class="grammar-input" data-answer="era" placeholder="..."/></td></tr>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="eras" placeholder="..."/></td></tr>'
            '<tr><td><b>\u00e9l/ella/usted</b></td><td><input type="text" class="grammar-input" data-answer="era" placeholder="..."/></td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="\u00e9ramos" placeholder="..."/></td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="erais" placeholder="..."/></td></tr>'
            '<tr><td><b>ellos/ellas/ustedes</b></td><td><input type="text" class="grammar-input" data-answer="eran" placeholder="..."/></td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<h3>3. \u672a\u5b8c\u6210\u8fc7\u53bb\u65f6\uff08\u63cf\u8ff0\u8fc7\u53bb\u7684\u72b6\u6001\u3001\u80cc\u666f\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td>yo</td><td><b>era</b></td></tr>'
            '<tr><td>t\u00fa</td><td><b>eras</b></td></tr>'
            '<tr><td>\u00e9l/ella/usted</td><td><b>era</b></td></tr>'
            '<tr><td>nosotros/as</td><td><b>\u00e9ramos</b></td></tr>'
            '<tr><td>vosotros/as</td><td><b>erais</b></td></tr>'
            '<tr><td>ellos/ellas/ustedes</td><td><b>eran</b></td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\U0001f4a1 \u6ce8\u610f\u91cd\u97f3\uff1a</b>'
            '<ul>'
            '<li><code>nosotros</code> \u5f62\u5f0f\u662f <code>\u00e9ramos</code>\uff0c\u5e26\u91cd\u97f3\u7b26\u53f7\uff08Esdr\u00fajula\uff0c\u7b26\u5408\u4f60\u4e4b\u524d\u603b\u7ed3\u7684\u89c4\u5219\u4e09\uff09</li>'
            '<li><code>vosotros</code> \u662f <code>erais</code>\uff0c<b>\u6ca1\u6709\u91cd\u97f3</b></li>'
            '</ul></div></div>'
        )
    },
    # Card 5: ser 简单将来时
    {
        "id": "GRAMMAR_ser_futuro",
        "episode": "",
        "scene_id": "",
        "line_index": 4,
        "character": "",
        "target_word": "ser \u00b7 \u7b80\u5355\u5c06\u6765\u65f6",
        "ipa": "",
        "pos": "grammar",
        "level": "A2",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u5c06\u6765\u65f6"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u7b80\u5355\u5c06\u6765\u65f6\u53d8\u4f4d\uff1aser\u00e9, ser\u00e1s, ser\u00e1, seremos, ser\u00e9is, ser\u00e1n",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u7b80\u5355\u5c06\u6765\u65f6",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u7b80\u5355\u5c06\u6765\u65f6\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>yo</b></td><td><input type="text" class="grammar-input" data-answer="ser\u00e9" placeholder="..."/></td></tr>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="ser\u00e1s" placeholder="..."/></td></tr>'
            '<tr><td><b>\u00e9l/ella/usted</b></td><td><input type="text" class="grammar-input" data-answer="ser\u00e1" placeholder="..."/></td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="seremos" placeholder="..."/></td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="ser\u00e9is" placeholder="..."/></td></tr>'
            '<tr><td><b>ellos/ellas/ustedes</b></td><td><input type="text" class="grammar-input" data-answer="ser\u00e1n" placeholder="..."/></td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<h3>4. \u7b80\u5355\u5c06\u6765\u65f6\uff08\u201c\u6211\u5c06\u4f1a\u662f\u201d\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td>yo</td><td><b>ser\u00e9</b></td></tr>'
            '<tr><td>t\u00fa</td><td><b>ser\u00e1s</b></td></tr>'
            '<tr><td>\u00e9l/ella/usted</td><td><b>ser\u00e1</b></td></tr>'
            '<tr><td>nosotros/as</td><td><b>seremos</b></td></tr>'
            '<tr><td>vosotros/as</td><td><b>ser\u00e9is</b></td></tr>'
            '<tr><td>ellos/ellas/ustedes</td><td><b>ser\u00e1n</b></td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\U0001f4a1 \u89c4\u5f8b\uff1a</b>'
            '<ul>'
            '<li>\u5c06\u6765\u65f6\u662f ser \u6700\u89c4\u5219\u7684\u65f6\u6001\u4e4b\u4e00\uff01\u76f4\u63a5\u5728\u539f\u5f62 <code>ser-</code> \u540e\u52a0\u6807\u51c6\u7ed3\u5c3e</li>'
            '<li>\u6240\u6709\u91cd\u97f3\u90fd\u5728\u7ed3\u5c3e\u4e0a\uff08\u9664 nosotros \u5916\uff09</li>'
            '</ul></div></div>'
        )
    },
    # Card 6: ser 虚拟式现在时
    {
        "id": "GRAMMAR_ser_subjuntivo",
        "episode": "",
        "scene_id": "",
        "line_index": 5,
        "character": "",
        "target_word": "ser \u00b7 \u865a\u62df\u5f0f\u73b0\u5728\u65f6",
        "ipa": "",
        "pos": "grammar",
        "level": "B1",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u865a\u62df\u5f0f"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u865a\u62df\u5f0f\u73b0\u5728\u65f6\u53d8\u4f4d\uff1asea, seas, sea, seamos, se\u00e1is, sean",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u865a\u62df\u5f0f\u73b0\u5728\u65f6",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u865a\u62df\u5f0f\u73b0\u5728\u65f6\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>yo</b></td><td><input type="text" class="grammar-input" data-answer="sea" placeholder="..."/></td></tr>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="seas" placeholder="..."/></td></tr>'
            '<tr><td><b>\u00e9l/ella/usted</b></td><td><input type="text" class="grammar-input" data-answer="sea" placeholder="..."/></td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="seamos" placeholder="..."/></td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="se\u00e1is" placeholder="..."/></td></tr>'
            '<tr><td><b>ellos/ellas/ustedes</b></td><td><input type="text" class="grammar-input" data-answer="sean" placeholder="..."/></td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<h3>5. \u865a\u62df\u5f0f\u73b0\u5728\u65f6\uff08\u8868\u8fbe\u613f\u671b\u3001\u6000\u7591\u3001\u5426\u5b9a\u547d\u4ee4\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td>yo</td><td><b>sea</b></td></tr>'
            '<tr><td>t\u00fa</td><td><b>seas</b></td></tr>'
            '<tr><td>\u00e9l/ella/usted</td><td><b>sea</b></td></tr>'
            '<tr><td>nosotros/as</td><td><b>seamos</b></td></tr>'
            '<tr><td>vosotros/as</td><td><b>se\u00e1is</b></td></tr>'
            '<tr><td>ellos/ellas/ustedes</td><td><b>sean</b></td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\U0001f4a1 \u6781\u5176\u4e0d\u89c4\u5219\uff1a</b>'
            '<ul>'
            '<li>\u8bcd\u6839\u53d8\u6210\u4e86 <code>se-</code>\uff0c\u5b8c\u5168\u4e0d\u50cf ser</li>'
            '<li><code>sea</code> \u548c <code>seas</code> \u5728\u53e3\u8bed\u91cc\u975e\u5e38\u9ad8\u9891\uff0c\u6bd4\u5982 <code>No creo que sea...</code>\uff08\u6211\u4e0d\u89c9\u5f97\u90a3\u662f...\uff09</li>'
            '</ul></div></div>'
        )
    },
    # Card 7: ser 命令式
    {
        "id": "GRAMMAR_ser_imperativo",
        "episode": "",
        "scene_id": "",
        "line_index": 6,
        "character": "",
        "target_word": "ser \u00b7 \u547d\u4ee4\u5f0f",
        "ipa": "",
        "pos": "grammar",
        "level": "B1",
        "pronunciation_focus": "vowel_a",
        "tags": ["\u8bed\u6cd5", "\u52a8\u8bcd\u53d8\u4f4d", "ser", "\u547d\u4ee4\u5f0f"],
        "sentence_cloze": "",
        "sentence_full": "",
        "translation": "ser \u7684\u547d\u4ee4\u5f0f\u53d8\u4f4d\uff1as\u00e9, sea, seamos, sed, sean",
        "sentence_translation": "",
        "cultural_note": "",
        "screenshot": "",
        "frequency_rank": None,
        "is_example_sentence": False,
        "grammar_topic": "ser \u00b7 \u547d\u4ee4\u5f0f",
        "grammar_front_html": (
            '<div class="grammar-quiz">'
            '<p class="quiz-instruction">\u586b\u5199 ser \u5728\u547d\u4ee4\u5f0f\u7684\u53d8\u4f4d\uff1a</p>'
            '<table class="grammar-quiz-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td><b>t\u00fa</b></td><td><input type="text" class="grammar-input" data-answer="s\u00e9" placeholder="..."/></td></tr>'
            '<tr><td><b>usted</b></td><td><input type="text" class="grammar-input" data-answer="sea" placeholder="..."/></td></tr>'
            '<tr><td><b>nosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="seamos" placeholder="..."/></td></tr>'
            '<tr><td><b>vosotros/as</b></td><td><input type="text" class="grammar-input" data-answer="sed" placeholder="..."/></td></tr>'
            '<tr><td><b>ustedes</b></td><td><input type="text" class="grammar-input" data-answer="sean" placeholder="..."/></td></tr>'
            '</tbody></table>'
            '<div class="quiz-check-hint">\u586b\u5199\u5b8c\u6210\u540e\u70b9\u51fb\u5361\u7247\u68c0\u67e5\u7b54\u6848</div>'
            '</div>'
        ),
        "grammar_content": (
            '<div class="grammar-card">'
            '<h3>6. \u547d\u4ee4\u5f0f\uff08\u76f4\u63a5\u547d\u4ee4\uff09</h3>'
            '<table class="grammar-table">'
            '<thead><tr><th>\u4eba\u79f0</th><th>\u53d8\u4f4d</th></tr></thead>'
            '<tbody>'
            '<tr><td>t\u00fa</td><td><b>s\u00e9</b></td><td>(\u201c\u4f60\u8981\u4e56/\u4f60\u8981\u5f53...\u201d)</td></tr>'
            '<tr><td>usted</td><td><b>sea</b></td></tr>'
            '<tr><td>nosotros/as</td><td><b>seamos</b></td></tr>'
            '<tr><td>vosotros/as</td><td><b>sed</b></td></tr>'
            '<tr><td>ustedes</td><td><b>sean</b></td></tr>'
            '</tbody></table>'
            '<div class="grammar-tip"><b>\u26a0\ufe0f \u6ce8\u610f\uff1a</b>'
            '<ul>'
            '<li><code>t\u00fa</code> \u7684\u547d\u4ee4\u5f0f\u662f <code>s\u00e9</code>\uff08\u5e26\u91cd\u97f3\u7b26\u53f7\uff0c\u533a\u5206 <code>se</code> \u81ea\u8eab\u4ee3\u8bcd\uff09</li>'
            '<li><code>vosotros</code> \u7684\u547d\u4ee4\u5f0f\u662f <code>sed</code>\uff08\u6781\u5176\u7279\u6b8a\uff0c\u4e0d\u89c4\u5219\uff09</li>'
            '</ul></div></div>'
        )
    }
]

with open('src/data/grammar_cards.json', 'w', encoding='utf-8') as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print(f"Generated {len(cards)} grammar cards successfully")
