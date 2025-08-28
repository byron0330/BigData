# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YahoonewsItem(scrapy.Item):
    url = scrapy.Field()           # 新聞連結
    title = scrapy.Field()         # 新聞標題
    author = scrapy.Field()        # 作者 (內頁取得)
    time = scrapy.Field()  # 發布時間 (內頁取得)
    minutes_ago = scrapy.Field()
    content = scrapy.Field()           # <— 新增：內文
    sentiment_label = scrapy.Field()   # <— pipeline 會填
    pass
