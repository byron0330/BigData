from pymongo import MongoClient

class MongoHelper:
    def __init__(self, uri="mongodb+srv://byron03227:facebook0000@cluster0.yodekge.mongodb.net/", db_name="FB-Post", collection_name="FaceBookPostData"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def ping(self):
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def save_one(self, data: dict):
        return str(self.collection.insert_one(data).inserted_id)

    def find_all(self, limit=10):
        return list(self.collection.find().limit(limit))

    def find_by_type(self, type_value: str):
        return list(self.collection.find({"Type": type_value}))
