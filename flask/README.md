# 🕷️ Crawler API

本專案是一個基於 **Flask + MongoDB** 的查詢服務，提供爬蟲產生的貼文與留言資料的 API。  
所有資料由內部爬蟲寫入 MongoDB，本 API 對外僅提供 **唯讀查詢** 功能。

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

```bash
python app.py
```

預設服務啟動於：  
👉 <http://127.0.0.1:5000>

---

## 📘 API 說明文件

### 1. 健康檢查
**GET** `/ping`  
測試 API 與資料庫是否連線正常。  

**回傳**
```json
{"status": "ok"}
```

---

### 2. 撈全部文件
**GET** `/all`

一次撈取所有文件（Post 與 Comment 皆包含）。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `limit` | int | 10 | 單次回傳筆數 (1~100) |
| `skip`  | int | 0  | 跳過筆數 |

**範例**
```
GET /all?limit=5&skip=0
```

---

### 3. 貼文列表
**GET** `/posts`

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
GET /posts?limit=3&include=comments&comments_limit=2
```

---

### 4. 單篇貼文詳情
**GET** `/posts/<post_id>`

取得單篇貼文內容，並支援留言分頁。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `comments_limit` | int | 50 | 每次回傳留言數，上限 200 |
| `comments_skip` | int | 0  | 跳過留言筆數 |

**範例**
```
GET /posts/acaf4c94-8cb9-4126-bf50-03045b9ba467?comments_limit=5&comments_skip=0
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
