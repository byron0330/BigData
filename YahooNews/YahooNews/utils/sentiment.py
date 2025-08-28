# -*- coding: utf-8 -*-
import re
from pathlib import Path

NEGATORS = {"不","沒","無","未","非","別","勿","不能","無法","未能"}
DEGREE = {"非常":1.5,"極其":1.5,"相當":1.3,"很":1.2,"較":1.1,"有點":0.8,"稍微":0.8}
HEDGES = {"疑","傳","或","恐","疑似","據稱","傳出","傳聞"}
MEDIA_NEG = {"爆發","惡化","抨擊","譴責","下台","撤職","違規","詐騙","失職","黑箱"}
MEDIA_POS = {"創新","突破","成長","改善","獲利","得獎","通過","升級","優化"}

def load_words(path: Path):
    with path.open(encoding="big5") as f:
        return set(w.strip() for w in f if w.strip())

def tokenize(text: str):
    return re.findall(r"[\u4e00-\u9fff]+", text or "")

def _window_weight(tokens, i):
    w = 1.0
    for j in range(max(0, i-2), i):
        t = tokens[j]
        if t in DEGREE: w *= DEGREE[t]
        if t in NEGATORS: w *= -1
        if t in HEDGES: w *= 0.8
    return w

def lexicon_score(text: str, pos_set, neg_set, fin_pos=None, fin_neg=None, topic="general"):
    tokens = tokenize(text)
    s = 0.0
    for i, t in enumerate(tokens):
        w = _window_weight(tokens, i)
        if t in pos_set or t in MEDIA_POS: s += 1.0 * w
        elif t in neg_set or t in MEDIA_NEG: s -= 1.0 * w
        if topic == "finance":
            if fin_pos and t in fin_pos: s += 1.0 * w
            if fin_neg and t in fin_neg: s -= 1.0 * w
    return s

def is_finance(title: str, content: str) -> bool:
    kw = {"股","台股","上市櫃","財報","營收","匯率","利率","通膨","晶片","AI","供應鏈","美元","大盤","標普","那斯達克","漲停","跌停"}
    text = (title or "") + " " + (content or "")
    return any(k in text for k in kw)

def article_sentiment(title: str, content: str, pos_set, neg_set, fin_pos=None, fin_neg=None):
    topic = "finance" if is_finance(title, content) else "general"

    def sentence_score(s: str):
        base = lexicon_score(s, pos_set, neg_set, fin_pos, fin_neg, topic)
        if "「" in s and "」" in s: base *= 0.8
        if any(h in s for h in HEDGES): base *= 0.8
        return base

    title_s = sentence_score(title) * 1.5
    sentences = [x for x in re.split(r"[。！？!?]\s*", content or "") if x.strip()]
    body = [sentence_score(s) for s in sentences] or [0.0]
    body_avg = sum(body)/len(body)
    score = (title_s + body_avg)/2  # 可正可負
    label = "pos" if score > 0.1 else "neg" if score < -0.1 else "neu"
    prob = round((score + 1)/2, 4)   # 映射 0~1
    return label, prob, score
