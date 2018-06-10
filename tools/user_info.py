import datetime
import time

import bcrypt
from pymongo import MongoClient

from tools import config

credentials = config.CredentialsManager()
client = MongoClient(credentials.get_mongo_credentials())
db = client.drivelog
users = db.users





def get_start_time(username):
    if check_username(username):
        for drive in users.find_one({"username": username})["drives"]:
            if drive["active"]:
                return drive["startTime"]
        return time.time()


def get_date_goal(username):
    if check_username(username):
        return users.find_one({"username": username})["date_goal"]
    else:
        return ""


def get_goal(username):
    if check_username(username):
        return users.find_one({"username": username})["goal"]
    else:
        return ""


def get_night_goal(username):
    if check_username(username):
        return users.find_one({"username": username})["night_goal"]
    else:
        return ""


def get_user(username):
    if check_username(username):
        return users.find_one({"username": username})
