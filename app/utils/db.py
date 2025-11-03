import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv() # Muat variabel dari file .env

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = os.environ.get('DB_NAME')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Definisikan 4 collections utama Anda
    assets_collection = db['assets']
    inventory_collection = db['inventory']
    schedules_collection = db['schedules']
    work_orders_collection = db['work_orders']

    print("Koneksi ke MongoDB Atlas berhasil...")
except Exception as e:
    print(f"Error koneksi ke MongoDB: {e}")
    client = None
    db = None