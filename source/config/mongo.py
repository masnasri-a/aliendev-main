import pymongo
import configparser

def connect():
    # Membaca konfigurasi dari file config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Mendapatkan konfigurasi koneksi ke MongoDB dari file config.ini
    mongodb_uri = config.get("MONGODB", "uri")
    mongodb_database = config.get("MONGODB", "database")

    # Membuat koneksi ke MongoDB
    client = pymongo.MongoClient(mongodb_uri)
    db = client[mongodb_database]

    return client,db