import bcrypt
from pymongo import MongoClient

from tools import config, user_check, user_get, time_manage, email_tool

credentials = config.CredentialsManager()
client = MongoClient(credentials.get_mongo_credentials())
db = client.drivelog
users = db.users


def register(username, email, password, timezone):
    if not user_check.check_username(username):
        password = password.encode()
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        password = password.decode()
        goal_date = time_manage.iso_utc_in_1_year()
        users.insert_one(
            {"username": username, "email": email, "password": password, "timezone": timezone, "verified": False,
             "verify_token": "", "date_goal": goal_date, "night_goal": 10, "goal": 50, "activeDrive": False,
             "drives": []})
        email_tool.send_email_confirmation(username)
        if user_check.check_username(username):
            return True
        else:
            return False
    else:
        return False


def remove_user(username):
    users.remove({"username": username})
    return not user_check.check_username(username)


def start_drive(username):
    if user_check.check_username(username):
        users.update_one({"username": username}, {"$set": {"activeDrive": True}})
        id = len(users.find_one({"username": username})["drives"])
        users.update_one({"username": username},
                         {"$push": {
                             "drives": {"startTime": time_manage.iso_utc_now(), "stopTime": 0, "active": True,
                                        "conditions": []}}})
        return user_get.get(username, "activeDrive")
    else:
        return False


def stop_drive(username, time_mode):
    if user_check.check_username(username):
        users.update_one({"username": username}, {"$set": {"activeDrive": False}})
        users.update_one({"username": username, "drives.active": True},
                         {"$set": {"drives.$.stopTime": time_manage.iso_utc_now()}})
        if time_mode == "night":
            users.update_one({"username": username, "drives.active": True},
                             {"$set": {"drives.$.conditions": ["night"]}})
        users.update_one({"username": username, "drives.active": True}, {"$set": {"drives.$.active": False}})
        return not user_get.get(username, "activeDrive")
    else:
        return False


def update_settings(username, date_goal, goal, night_goal):
    if int(goal) <= 0:
        return False
    if int(night_goal) <= 0:
        return False
    if user_check.check_username(username):
        users.update_one({"username": username},
                         {"$set": {"date_goal": time_manage.date_local_to_iso_utc(username, date_goal), "goal": goal,
                                   "night_goal": night_goal}})
        return True
    else:
        return False


def update_drive(username, drive_id, start_date, start_time, stop_time, conditions):
    if user_check.check_username(username):
        updated_drive_info = time_manage.date_start_stop_to_iso_utc(username, start_date, start_time, stop_time)
        users.update_one({"username": username},
                         {"$set": {f"drives.{drive_id}.startTime": updated_drive_info["start_date"]
                                   }})
        users.update_one({"username": username},
                         {"$set": {f"drives.{drive_id}.stopTime": updated_drive_info["stop_date"]}})
        users.update_one({"username": username}, {"$set": {f"drives.{drive_id}.conditions": conditions}})
        return True
    return False


def remove_drive(username, drive_id):
    if user_check.check_username(username):
        start_time = users.find_one({"username": username})["drives"][int(drive_id)]["startTime"]
        users.update_one({"username": username}, {"$pull": {"drives": {"startTime": start_time}}})


def create_drive(username):
    if user_check.check_username(username):
        users.update_one({"username": username}, {"$push": {
            "drives": {"startTime": time_manage.iso_utc_now(), "stopTime": time_manage.iso_utc_now(), "active": False,
                       "conditions": []}}})


def associate_token(username, token):
    if user_check.check_username(username):
        users.update_one({"username": username}, {"$set": {"verify_token": token}})


def verify_user(username, token):
    if user_check.check_username(username):
        if user_get.get(username, "verify_token") == token:
            users.update_one({"username": username}, {"$set": {"verified": True}})
            return True
        else:
            return False
    else:
        return False
