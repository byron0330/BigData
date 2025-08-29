# 🕷️ Crawler API

本專案是一個基於 **Flask + MongoDB** 的查詢服務，提供爬蟲產生的貼文與留言資料的 API。  
所有資料由內部爬蟲寫入 MongoDB，本 API 對外僅提供 **唯讀查詢** 功能。

---
## 📂 專案結構
crawler-api/
├── app.py               # Flask 主程式
├── mongo_helper.py      # MongoDB 輔助方法
├── requirements.txt     # 套件需求
├── README.md            # 專案說明文件
└── ...
---
## 🚀 環境需求

- Python 3.9+
- MongoDB 5.0+
- pip 套件管理工具

---

## 📦 安裝

1. 下載專案
   ```bash
   git clone https://github.com/your-repo/crawler-api.git
   cd crawler-api
   ```

2. 建立虛擬環境並安裝套件
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows

   pip install -r requirements.txt
   ```

3. 確認 `mongo_helper.py` 內已設定好正確的 MongoDB 連線字串。

---

## ▶️ 啟動服務

本專案已部屬至 Azure Web App，不需手動啟動服務。

服務已固定運行於以下網址：
👉 https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net

你可以直接透過上述網址呼叫 API，例如：

健康檢查：GET /ping

撈取資料：GET /all、GET /posts、GET /posts/<post_id>

## 📘 API 說明文件

### 1. 健康檢查
**GET** `https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/ping`  
測試 API 與資料庫是否連線正常。  

**回傳**
```json
{"status": "ok"}
```

---

### 2. 撈全部文件
**GET** `https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/all`

一次撈取所有文件（Post 與 Comment 皆包含）。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `limit` | int | 10 | 單次回傳筆數 (1~100) |
| `skip`  | int | 0  | 跳過筆數 |

**範例**
```
GET https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/all?limit=5&skip=0
```

---

### 3. 貼文列表
**GET** `https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/posts`

列出所有貼文（`Type=Post`），依建立時間新 → 舊排序。  
可選擇性帶回部分留言預覽。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `limit` | int | 10 | 單次回傳筆數 (1~100) |
| `skip` | int | 0 | 跳過筆數 |
| `include` | string | - | 設為 `comments` 時會帶回部分留言 |
| `comments_limit` | int | 0 | 搭配 `include=comments` 使用，最多 50 |

**範例**
```
GET https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/posts?limit=3&include=comments&comments_limit=2
```
**回應**
```json
{
  "data": [
    {
      "_id": "66cfbd8c8f0d45e4f7c12345",
      "Type": "Post",
      "PostId": "acfa4c94-8cb9-4126-bf50-03045b9ba467",
      "Author": "LAVA 鐵人公司",
      "Content": "2026第一天，一起去跑步～...",
      "comment_count": 2,
      "comments": [
        {
          "_id": "68afe1c1e047d2ce774d7def",
          "Type": "Comment",
          "Author": "Johnny Huang",
          "Content": "太可惜了沒有42K的"
        },
        {
          "_id": "68afe1bde047d2ce774d7dee",
          "Type": "Comment",
          "Author": "饅頭",
          "Content": "貼圖"
        }
      ]
    }
  ],
  "meta": {
    "count": 1,
    "has_next": true,
    "limit": 1,
    "skip": 0,
    "total_count": 554
  }
}
```

---

### 4. 單篇貼文詳情
**GET** `https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/posts/<post_id>`

取得單篇貼文內容，並支援留言分頁。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `comments_limit` | int | 50 | 每次回傳留言數，上限 200 |
| `comments_skip` | int | 0  | 跳過留言筆數 |

**範例**
```
GET https://facebook-flask-api-bjgrggesf0hnd6ez.southeastasia-01.azurewebsites.net/posts/c6c97327-94ac-45dd-831f-fb03c0817d48?comments_limit=5&comments_skip=0
```
**回應**
```json
{
  "Author": "永續跑者倡議行動",
  "Content": "路跑賽事廢棄物減量大哉問！如何\n才能達成「零廢棄物」的終極目標\n？\n當路跑人潮退去，留下的只有處理不完的垃圾？廢棄\n物如何減量與回收，正是檢驗一場賽事能否邁向永續\n的關鍵，文章提出四大重要議題，思考路跑賽事如何\n從源頭管控到末端回收，達成「零廢棄物」的終極目\n標。",
  "CreatedAt": "2025-08-27T14:57:20.981000",
  "PostId": "c6c97327-94ac-45dd-831f-fb03c0817d48",
  "Type": "Post",
  "_id": "68afe1e5e047d2ce774d7df5",
  "comment_count": 1,
  "comments": [
    {
      "Author": "鐵路大亨",
      "Content": "務實一點，零廢棄物只是口號，40%(舉例\n)可能比較實在，",
      "CreatedAt": "2025-08-27T15:57:20.981000",
      "PostId": "c6c97327-94ac-45dd-831f-fb03c0817d48",
      "Type": "Comment",
      "_id": "68afe1e1e047d2ce774d7df4"
    }
  ]
}
```
---

## 🔒 設計說明

- 所有 API **唯讀**：資料由爬蟲 pipeline 寫入 MongoDB，不提供對外寫入。  
- **防護**：限制 `limit` / `comments_limit` 上限，避免一次拉取過多資料。  
- **排序**：所有列表皆依 `CreatedAt` 新 → 舊。  
- **序列化**：`ObjectId` 與 `datetime` 轉換為字串，確保 JSON 可直接使用。  

---

## 📑 待辦 / 改進方向

- [ ] 加入查詢條件（依作者、時間範圍等）  
- [ ] 加入 API 驗證（Token 或 Key）  

---
