# Facebook Group Crawler

本專案使用 **Selenium + Chrome WebDriver**，模擬手機版 Facebook (m.facebook.com)，抓取指定社團三個月內的貼文與留言，並將資料存入 MongoDB。

---

## 專案完成時間與資料範圍
- 本專案於 **2025/08/28 11:00 左右**完成。  
- 因此目前 MongoDB 中提供的資料，僅包含 **2025/08/28 11:00 以前**，且**限定近三個月內**的貼文與留言。  
- 若要取得更新的資料，請重新執行 `FacebookCraw.py` 並確保 `cookies.json` 與 MongoDB 連線設定正確。


## 功能特色
- **抓取貼文 (Post)**：包含作者、內容、時間、隨機生成的 `PostId`。  
- **抓取留言 (Comment)**：包含留言作者、留言內容、留言時間，並與 `PostId` 建立關聯。  
- **自動展開「查看更多」**：點擊 Facebook 貼文或留言中的「查看更多」按鈕以獲取完整內容。  
- **模擬手機裝置**：使用 `iPhone 12 Pro` 的 mobile emulation，提高抓取穩定性。  
- **MongoDB 存儲**：透過 `MongoHelper` 將資料存入 MongoDB。  

---

## 環境需求

- Python 3.10+  
- Google Chrome 瀏覽器  
- MongoDB 資料庫  

安裝套件：
```bash
pip install -r requirements.txt
