# YahooNews/spiders/yahoospider_api.py
import json
from datetime import datetime , timezone ,timedelta
from urllib.parse import quote, urlencode
import scrapy
from YahooNews.items import YahoonewsItem 
class YahooApiSpider(scrapy.Spider):
    startTime = datetime.now(timezone(timedelta(hours=8)))
    name = "yahoospider_api"
    allowed_domains = ["tw.news.yahoo.com"]
    BASE = "https://tw.news.yahoo.com/_td-news/api/resource"
    hit_old = True
    # 你可以在這裡調整一次抓幾筆、從哪個 offset 開始、最多翻幾頁
    page_size = 20
    start_offset = 0

    custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://tw.news.yahoo.com/"
    }

    def build_url_parts(self, count=20, start=0, document_type="article", tag=None):
        """
        產生 (path, querystring dict)
        path: 內含 matrix params 的完整路徑
        qs:   一般 query string 參數 (dict)
        """
        ncp = {
            "query": {
                "count": count,
                "imageSizes": "220x128",
                "documentType": document_type,  # e.g. "article" or "article,video"
                "start": start,
                "tag": tag
            }
        }
        ncp_str = json.dumps(ncp, separators=(',', ':'))
        ncp_enc = quote(ncp_str, safe='')  # 放到 path 的 matrix 參數要全部編碼

        path = f"{self.BASE}/ListService;api=archive;ncpParams={ncp_enc}"

        qs = {
            "bkt": '["c1-twnews-pc-cg","prebid-ver9-53update-apac-test"]',
            "device": "desktop",
            "ecma": "modern",
            "feature": "oathPlayer,enableEvPlayer,enableGAMAds,enableGAMEdgeToEdge,useCGReady,videoDocking",
            "intl": "tw",
            "lang": "zh-Hant-TW",
            "partner": "none",
            "region": "TW",
            "site": "news",
            "tz": "Asia/Taipei",
            "ver": "2.3.3112",
            "returnMeta": "true",
        }
        return path, qs

    def start_requests(self):
        start = self.start_offset
        path, qs = self.build_url_parts(count=self.page_size, start=start, document_type="article,video")
        url = f"{path}?{urlencode(qs)}"
        yield scrapy.Request(
            url=url,
            headers=self.custom_headers,
            callback=self.parse_api_json,
            cb_kwargs={"start": start, "page_index": 1},
        )

    def parse_api_json(self, response, start, page_index):
        data = response.json()
        items = data["data"]

        for it in reversed(items):
            # 1) 先組列表欄位
            detail_url = "https://tw.news.yahoo.com" + it.get("url")
            news_item = YahoonewsItem()
            news_item["title"] = it.get("title")
            news_item["url"] = detail_url
            # 2) 再去詳細頁補資料
            yield response.follow(
                url=detail_url,
                headers=self.custom_headers,
                callback=self.parse_detail,
                cb_kwargs={"item": news_item},
                dont_filter=True,
                priority=10,
            )
            

        if self.hit_old:
            next_start = start + self.page_size
            path, qs = self.build_url_parts(count=self.page_size, start=next_start, document_type="article")
            next_url = f"{path}?{urlencode(qs)}"
            yield scrapy.Request(
                url=next_url,
                headers=self.custom_headers,
                callback=self.parse_api_json,
                cb_kwargs={"start": next_start, "page_index": page_index + 1},
            )

    def parse_detail(self, response, item: YahoonewsItem):
        """在詳細頁抓 內文 + 發布時間，補回到 item 再 yield"""
        # --- 內文 (Yahoo TW 常見為 caas-body) ---
        # 盡量健壯，多給幾個 fallback selector
        author = response.xpath('/html/body/div[3]/div/main/div/section[1]/div/article/header/div[2]/div[1]/div/div[1]//text()').get()
        time_str = response.xpath('/html/body/div[3]/div/main/div/section[1]/div/article/header/div[2]/div[1]/div/div[2]/div/time/@datetime').get()
        if time_str == None:
            time_str = response.xpath('/html/body/div[3]/div/main/div/section[1]/div/article/header/div[2]/div[1]/div/div[3]/div/time/@datetime').get()
        
        if time_str ==None:
            time_str = response.xpath('/html/body/div[3]/div/main/div/section[1]/div/article/header/div[3]/div[1]/div/div[2]/div/time/@datetime').get()

        content_list = response.xpath('/html/body/div[3]/div/main/div/section[1]/div/article/div//text()').getall()
        content = "".join(text.strip() for text in content_list if text.strip())
        
        if time_str:
            try:
                # 把 "Z" (UTC) 換成 +00:00
                dt_utc = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                # 轉成台灣時間
                published_at_tw = dt_utc.astimezone(timezone(timedelta(hours=8)))
                # 格式化成 YYYY/MM/DD HH:mm
                published_at_tw_str = published_at_tw.strftime("%Y/%m/%d %H:%M")
            except Exception as e:
                self.logger.warning(f"time parse fail: {e} raw={time_str}")

        item["author"] = (author or "").strip() or None
        item["time"] = published_at_tw_str
        item["content"] = content
        if self.is_within_last_hour(item["time"]):
            yield item
        else:
            self.hit_old = False
        
    
    def is_within_last_hour(self, time_str: str) -> bool:
        """檢查文章時間是否在啟動時間前 1 小時內"""
        if not time_str:
            return False
        try:
            if "T" in time_str:  
                # ISO 格式
                dt_utc = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                published_at = dt_utc.astimezone(timezone(timedelta(hours=8)))
            else:
                # 已格式化的台北時間字串
                dt_local = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
                published_at = dt_local.replace(tzinfo=timezone(timedelta(hours=8)))

            return published_at >= (self.startTime - timedelta(hours=1))
        except Exception as e:
            self.logger.warning(f"time parse fail: {e} raw={time_str}")
            return False