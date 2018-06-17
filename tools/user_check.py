from pymongo import MongoClient
from tools import config
import bcrypt
credentials = config.CredentialsManager()
client = MongoClient(credentials.get_mongo_credentials())
db = client.drivelog
users = db.users


def check_username(username):
    if users.find_one({"username": username}):
        return True
    else:
        return False


def check_email(email):
    if users.find_one({"email": email}):
        return True
    else:
        return False


def check_password(username, password):
    if check_username(username):
        retrieved_password = users.find_one({"username": username})['password']
        retrieved_password = retrieved_password.encode()
        password = password.encode()
        return bcrypt.checkpw(password, retrieved_password)
    else:
        return False


def check_drive(username):
    if check_username(username):
        return users.find_one({"username": username})["activeDrive"]
    else:
        return False


def check_verified(username):
    if check_username(username):
        return users.find_one({"username": username})["verified"]
    return False