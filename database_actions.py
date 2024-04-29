#import logging
#from pymongo import MongoClient
#
#class Database:
#    def __init__(self, uri, db_name, collection_name):
#        try:
#            self.client = MongoClient(uri)  # MongoDB default connection
#            self.db = self.client[db_name]
#            self.collection = self.db[collection_name]
#        except Exception as e:
#            logging.error(e)
#            raise e
#
#    def add_one(self, document):
#        """Inserts one document into the collection."""
#        result = self.collection.insert_one(document)
#        return result.inserted_id
#
#    def add_many(self, documents):
#        """Inserts multiple documents into the collection."""
#        result = self.collection.insert_many(documents)
#        return result.inserted_ids
#
#    def get_all_data(self):
#        """Retrieves all documents from the collection."""
#        return list(self.collection.find({}))
#
#    def __del__(self):
#        """Destructor to close the MongoDB client."""
#        self.client.close()


import logging
import motor.motor_asyncio
from pymongo.server_api import ServerApi
from fastapi import HTTPException, status

class Database:
    def __init__(self, uri, db_name, collection_name):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(uri, server_api=ServerApi('1'), tls=True)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except Exception as e:
            logging.error(e)
            raise e

    async def add_one(self, document):
        """Inserts one document into the collection."""
        result = await self.collection.insert_one(document)
        return result.inserted_id

    async def add_many(self, documents):
        """Inserts multiple documents into the collection."""
        result = await self.collection.insert_many(documents)
        return result.inserted_ids

    async def get_all_data(self):
        """Retrieves all documents from the collection."""
        try:
            cursor = self.collection.find({})
            return [document async for document in cursor]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{e}",
            )

    def __del__(self):
        """Destructor to close the MongoDB client."""
        self.client.close()
