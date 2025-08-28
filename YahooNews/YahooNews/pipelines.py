# -*- coding: utf-8 -*-
from pathlib import Path
from itemadapter import ItemAdapter
from YahooNews.utils.sentiment import load_words, article_sentiment
from scrapy.exceptions import DropItem

class SentimentPipeline:
    def open_spider(self, spider):
        base = Path(__file__).resolve().parent
        data_dir = base / "data"
        self.POS = load_words(data_dir / "NTUSD_positive.txt")
        self.NEG = load_words(data_dir / "NTUSD_negative.txt")
        fin_pos_p = data_dir / "NTUSD_Fin_positive.txt"
        fin_neg_p = data_dir / "NTUSD_Fin_negative.txt"
        self.FIN_POS = load_words(fin_pos_p) if fin_pos_p.exists() else None
        self.FIN_NEG = load_words(fin_neg_p) if fin_neg_p.exists() else None

    def process_item(self, item, spider):
        ad = ItemAdapter(item)
        title = ad.get("title") or ""
        content = ad.get("content") or ""
        label, prob, raw = article_sentiment(title, content, self.POS, self.NEG, self.FIN_POS, self.FIN_NEG)

        label_map = {"pos": "正向", "neu": "中性", "neg": "負向"}
        ad["sentiment_label"] = label_map.get(label, "中性")
        return item

class DuplicatesPipeline:
    """避免重複資料"""
    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        ad = ItemAdapter(item)
        key = ad.get("url") or ad.get("title")
        if not key:
            return item

        if key in self.seen:
            raise DropItem(f"Duplicate item found: {key}")
        self.seen.add(key)
        return item