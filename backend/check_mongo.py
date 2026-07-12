from config import ActiveConfig
from pymongo import MongoClient
import sys

def main():
    uri = ActiveConfig.MONGO_URI
    print("Using MONGO_URI:", uri)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("PING_OK")
    except Exception as e:
        print("PING_FAILED:", type(e).__name__, str(e))
        sys.exit(2)

if __name__ == '__main__':
    main()
