from pymongo import MongoClient, errors
from datetime import datetime, timedelta
class MongoHelper:
    def __init__(self, uri="mongodb+srv://byron03227:facebook0000@cluster0.yodekge.mongodb.net/", db_name="FB-Post", collection_name="test"):
        """
        初始化 Mongo 連線
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.three_months_ago = (datetime.now() - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0)
        
    def save_one(self, data: dict):
        """
        存單筆 dict
        """ 
        if not isinstance(data, dict):
            raise ValueError("data 必須是 dict")
        if data["CreatedAt"] > self.three_months_ago :
            result = self.collection.insert_one(data)
            return True
        else:
            return False

    def ping(self):
        """
        測試連線是否成功
        """
        try:
            self.client.admin.command("ping")
            return True
        except errors.ConnectionFailure:
            return False


    def save_many(self, data_list: list):
        """
        存多筆 [dict, dict, ...]
        """
        if not isinstance(data_list, list):
            raise ValueError("data_list 必須是 list")
        result = self.collection.insert_many(data_list)
        return result.inserted_ids

    def close(self):
        """
        關閉連線
        """
        self.client.close()
if __name__ == "__main__":
    mongo = MongoHelper(uri="mongodb+srv://byron03227:facebook0000@cluster0.yodekge.mongodb.net/", db_name="FB-Post", collection_name="FB-Post")

    if mongo.ping():
        print("✅ 已成功連線到 MongoDB")
    else:
        print("❌ 無法連線到 MongoDB")

    mongo.close()
