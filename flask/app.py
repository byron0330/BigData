from flask import Flask, request, jsonify
from mongo_helper import MongoHelper
from bson import ObjectId
app = Flask(__name__)
app.json.ensure_ascii = False   # ← 新版正確寫法
mongo = MongoHelper()

# JSON serializer 處理 ObjectId

from bson import ObjectId
from datetime import datetime

def serialize(obj):
    # list: 處理每一項
    if isinstance(obj, list):
        return [serialize(x) for x in obj]

    # dict: 遞迴處理每個欄位，_id 轉字串
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            else:
                out[k] = serialize(v)
        return out

    # 單值: 直接轉
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj



# 測試連線
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok" if mongo.ping() else "fail"})

# 撈全部 (限制筆數)
@app.get("/all")
def get_all():
    # 參數：limit(預設10、1~100之間)、skip(預設0)
    limit = request.args.get("limit", default=10, type=int)
    skip  = request.args.get("skip",  default=0,  type=int)

    # 邊界處理
    if limit is None: limit = 10
    if skip  is None: skip  = 0
    limit = max(1, min(limit, 100))  # 上限 100，避免一次撈太多
    skip  = max(0, skip)

    # 依建立時間新到舊排序（若你的 CreatedAt 是字串，建議存成 datetime 才能正確排序）
    cursor = (mongo.collection
                    .find({})
                    .sort("CreatedAt", -1)
                    .skip(skip)
                    .limit(limit))

    docs = [serialize(d) for d in cursor]

    return jsonify({
        "data": docs,
        "meta": {
            "count": len(docs),  # 本次回傳筆數
            "limit": limit,
            "skip": skip
        }
    })

@app.get("/posts")
def list_posts():
    limit = max(1, min(request.args.get("limit", 10, type=int), 100))
    skip  = max(0, request.args.get("skip", 0, type=int))
    include = request.args.get("include")  # "comments" or None
    comments_limit = max(0, min(request.args.get("comments_limit", 0, type=int), 50))

    base_match = {"Type": "Post"}

    pipeline = [
        {"$match": base_match},
        {"$sort": {"CreatedAt": -1}},
        {"$facet": {
            "total": [{"$count": "count"}],
            "data": [
                {"$skip": skip},
                {"$limit": limit},
                {"$lookup": {
                    "from": mongo.collection.name,
                    "let": {"pid": "$PostId"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$and": [
                                {"$eq": ["$PostId", "$$pid"]},
                                {"$eq": ["$Type", "Comment"]}
                            ]}
                        }},
                        {"$count": "count"}
                    ],
                    "as": "comment_stat"
                }},
                {"$addFields": {"comment_count": {"$ifNull": [{"$arrayElemAt": ["$comment_stat.count", 0]}, 0]}}},
                {"$project": {"comment_stat": 0}}
            ]
        }}
    ]

    if include == "comments" and comments_limit > 0:
        pipeline[-1]["$facet"]["data"].append({
            "$lookup": {
                "from": mongo.collection.name,
                "let": {"pid": "$PostId"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$and": [
                            {"$eq": ["$PostId", "$$pid"]},
                            {"$eq": ["$Type", "Comment"]}
                        ]}
                    }},
                    {"$sort": {"CreatedAt": 1}},
                    {"$limit": comments_limit}
                ],
                "as": "comments"
            }
        })

    faceted = list(mongo.collection.aggregate(pipeline))[0]
    total_count = faceted["total"][0]["count"] if faceted["total"] else 0
    docs = [serialize(d) for d in faceted["data"]]

    return jsonify({
        "data": docs,
        "meta": {
            "count": len(docs),
            "limit": limit,
            "skip": skip,
            "total_count": total_count,
            "has_next": skip + len(docs) < total_count
        }
    })


@app.get("/posts/<post_id>")
def get_post(post_id):
    comments_limit = max(0, min(request.args.get("comments_limit", 50, type=int), 200))
    comments_skip  = max(0, request.args.get("comments_skip", 0, type=int))

    pipeline = [
        {"$match": {"Type": "Post", "PostId": post_id}},
        {"$limit": 1},
        {"$lookup": { 
            "from": mongo.collection.name,
            "let": {"pid": "$PostId"},
            "pipeline": [
                {"$match": {
                    "$expr": {"$and": [
                        {"$eq": ["$PostId", "$$pid"]},
                        {"$eq": ["$Type", "Comment"]}
                    ]}
                }},
                {"$count": "count"}
            ],
            "as": "comment_stat"
        }},
        {"$addFields": {"comment_count": {"$ifNull": [{"$arrayElemAt": ["$comment_stat.count", 0]}, 0]}}},
        {"$project": {"comment_stat": 0}},
        {"$lookup": { 
            "from": mongo.collection.name,
            "let": {"pid": "$PostId"},
            "pipeline": [
                {"$match": {
                    "$expr": {"$and": [
                        {"$eq": ["$PostId", "$$pid"]},
                        {"$eq": ["$Type", "Comment"]}
                    ]}
                }},
                {"$sort": {"CreatedAt": 1}},
                {"$skip": comments_skip},
                {"$limit": comments_limit}
            ],
            "as": "comments"
        }}
    ]

    res = list(mongo.collection.aggregate(pipeline))
    if not res:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(serialize(res[0]))

if __name__ == "__main__":
    
    doc = mongo.collection.find_one({})
    app.run(debug=True, port=5000)