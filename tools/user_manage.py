import bcrypt
from pymongo import MongoClient
from tools import user_info
from datetime import datetime, timedelta
import time

client = MongoClient('mongodb://EngelGames:katze@195.201.156.29/drivelog')
db = client.drivelog
users = db.users


def register(username, email, password):
    if not user_info.check_username(username):
        password = password.encode()
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        password = password.decode()
        goal_date = (datetime.now() + timedelta(days=365)).__format__("%b %m, %Y")
        users.insert_one(
            {"username": username, "email": email, "password": password, "time_goal": goal_date, "night_goal": 10,
             "goal": 50, "activeDrive": False, "drives": []})
        if user_info.check_username(username):
            return True
        else:
            return False
    else:
        return False


def remove_user(username):
    users.remove({"username": username})
    return not user_info.check_username(username)


def start_drive(username):
    if user_info.check_username(username):
        users.update_one({"username": username}, {"$set": {"activeDrive": True}})
        id = len(users.find_one({"username": username})["drives"])
        users.update_one({"username": username},
                         {"$push": {
                             "drives": {"startTime": time.time(), "stopTime": 0, "active": True, "conditions": [],
                                        "id": id}}})
        return user_info.check_drive(username)
    else:
        return False


def stop_drive(username):
    if user_info.check_username(username):
        users.update_one({"username": username}, {"$set": {"activeDrive": False}})
        users.update_one({"username": username, "drives.active": True}, {"$set": {"drives.$.stopTime": time.time()}})
        users.update_one({"username": username, "drives.active": True}, {"$set": {"drives.$.active": False}})
        return not user_info.check_drive(username)
    else:
        return False


def update_settings(username, time_goal, goal, night_goal):
    if user_info.check_username(username):
        users.update_one({"username": username},
                         {"$set": {"time_goal": time_goal, "goal": goal, "night_goal": night_goal}})
        return True
    else:
        return False


def update_drive(username, id, start_time, stop_time):
    if user_info.check_username(username):
        users.update_one({"username": username}, {"$set": {f"drives.{id}.startTime": start_time}})
        users.update_one({"username": username}, {"$set": {f"drives.{id}.stopTime": stop_time}})
        return True
    return False


def remove_drive(username, id):
    if user_info.check_username(username):
        start_time = users.find_one({"username": username})["drives"][int(id)]["startTime"]
        users.update_one({"username": username}, {"$pull": {"drives": {"startTime": start_time}}})
    print(id)