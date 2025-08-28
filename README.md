# BigData 面試測驗作品集

此 Repo 收錄三個面試測驗專案，皆為獨立子專案，可分別進入資料夾查看。

---

## 📌 專案一：Yahoo 新聞爬蟲 (Scrapy)
- 於8/26 16:00時完成並執行
- 使用 Scrapy 框架抓取 Yahoo 新聞資料
- 內建 **輿情分析 Pipeline**（字典法）
- 自動輸出 CSV，包含：標題、連結、作者、日期、情緒標籤
- 📂 [進入專案](./YahooNews)

---

## 📌 專案二：Facebook 指定社團爬蟲 (Selenium + MongoDB)
- 使用 Selenium 模擬手機版 Facebook
- 自動展開「查看更多」、抓取貼文與留言
- 貼文與留言以 `PostId` 建立關聯，並存入 MongoDB
- ⚠️ MongoDB 目前連線為 **Test 環境**
- 📂 [進入專案](./Facebook)

---

## 📌 專案三：Flask API (Flask + MongoDB)
- 使用 Flask + MongoDB 提供 API 介面
- 支援資料插入、查詢等功能
- 已測試可部署到雲端 (Azure)
- 📂 [進入專案](./flask)

---

## 💡 使用方式
1. 進入各子專案資料夾
2. 依照 `README.md` 指示安裝環境與執行
