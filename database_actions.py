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

    async def get_data_except_element_which_is_in_db(self, value):
        """Retrieves all documents except the one with the specified key-value pair."""
        try:
            document = await self.collection.find_one({"vc name": value})
            if document and document["vc name"] != "Unknown":
                cursor = self.collection.find({"vc name": {"$ne": value}})
                return [document async for document in cursor]
            else:
                return await self.get_all_data()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{e}",
            )

    async def check_is_instance_in_db(self, value):
        """Checks if a certain key has a certain value in the collection."""
        try:
            document = await self.collection.find_one({"vc name": value})
            return document is not None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{e}",
            )

    def __del__(self):
        """Destructor to close the MongoDB client."""
        self.client.close()
