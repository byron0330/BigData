# YahooNews Scraper
此專案於08/26 16:00時完成
故範例excel檔案將提供 08/26 16:00 ~ 08/26 15:00之文章內容

本專案使用 **Scrapy** 框架，收錄 Yahoo 新聞近一小時的文章，並進行簡單的輿情分析（正向 / 中性 / 負向）。  

產出檔案為 `output/yahoo_news_08261600_done.csv`，包含：
- `title`：新聞標題  
- `url`：新聞連結  
- `author`：作者  
- `time`：發布時間（台灣時間）  
- `content`：新聞內文  
- `sentiment_label`：輿情分析標籤  

---

## 環境需求

- Python 3.10+  
- 安裝依賴套件：

```bash
pip install -r requirements.txt

