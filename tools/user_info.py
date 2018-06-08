import bcrypt
from pymongo import MongoClient
import time
import datetime

mongo_credentials = open("mongo.credentials", "r")
client = MongoClient(mongo_credentials.read())
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


def check_drive(username):
    if check_username(username):
        return users.find_one({"username": username})["activeDrive"]
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


def get_start_time(username):
    if check_username(username):
        for drive in users.find_one({"username": username})["drives"]:
            if drive["active"]:
                return drive["startTime"]
        return time.time()


def get_time_goal(username):
    if check_username(username):
        return users.find_one({"username": username})["time_goal"]
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


def get_drive_list(username):
    if check_username(username):
        return users.find_one({"username": username})["drives"]
    else:
        return []


def get_drive_data(username):
    if check_username(username):
        drive_list = get_drive_list(username)
        drive_data = []
        for drive in drive_list:
            start_time = drive["startTime"]
            stop_time = drive["stopTime"]
            format_start_date = datetime.datetime.fromtimestamp(start_time).__format__("%b %d, %Y")
            format_start_time = datetime.datetime.fromtimestamp(start_time).__format__("%I:%M %p")
            format_stop_time = datetime.datetime.fromtimestamp(stop_time).__format__("%I:%M %p")
            duration_hours = (round(stop_time - start_time)) // 3600
            remainder = (round(stop_time - start_time)) % 3600
            duration_minutes = remainder // 60
            remainder = remainder % 60
            duration_seconds = remainder
            if duration_hours < 10:
                duration_hours = "0" + str(duration_hours)
            if duration_minutes < 10:
                duration_minutes = "0" + str(duration_minutes)
            if duration_seconds < 10:
                duration_seconds = "0" + str(duration_seconds)
            duration = f"{duration_hours}:{duration_minutes}:{duration_seconds}"
            drive_data.append(
                {"startDate": format_start_date, "startTime": format_start_time, "stopTime": format_stop_time,
                 "duration": duration, "id": drive_list.index(drive), "conditions": drive["conditions"]})
        return drive_data


def get_drive(username, id):
    if check_username(username):
        drive = users.find_one({"username": username})["drives"][int(id)]
        start_time = drive["startTime"]
        stop_time = drive["stopTime"]
        format_start_date = datetime.datetime.fromtimestamp(start_time).__format__("%b %d, %Y")
        format_start_time = datetime.datetime.fromtimestamp(start_time).__format__("%I:%M %p")
        format_stop_time = datetime.datetime.fromtimestamp(stop_time).__format__("%I:%M %p")
        duration_hours = (round(stop_time - start_time)) // 3600
        remainder = (round(stop_time - start_time)) % 3600
        duration_minutes = remainder // 60
        remainder = remainder % 60
        duration_seconds = remainder
        if duration_hours < 10:
            duration_hours = "0" + str(duration_hours)
        if duration_minutes < 10:
            duration_minutes = "0" + str(duration_minutes)
        if duration_seconds < 10:
            duration_seconds = "0" + str(duration_seconds)
        duration = f"{duration_hours}:{duration_minutes}:{duration_seconds}"
        return {"startDate": format_start_date, "startTime": format_start_time, "stopTime": format_stop_time,
                "duration": duration, "id": get_drive_list(username).index(drive), "conditions": drive["conditions"]}


def get_stats(username):
    user = users.find_one({"username": username})
    total_time = 0
    night_time = 0
    for drive in user["drives"]:
        total_time += (drive["stopTime"] - drive["startTime"])
        if "night" in drive["conditions"]:
            night_time += (drive["stopTime"] - drive["startTime"])
    total_hours = round(total_time // 3600)
    total_minutes = round((total_time % 3600) / 60)
    total_info = f"{total_hours} hours {total_minutes} minutes"
    night_hours = round(night_time // 3600)
    night_minutes = round((night_time % 3600) / 60)
    night_info = f"{night_hours} hours {night_minutes} minutes"
    total_percent = str(round(((total_time / 3600) / int(user["goal"])) * 100)) + "%"
    night_percent = str(round(((night_time / 3600) / int(user["goal"])) * 100)) + "%"
    days_until_goal = round((time.mktime(time.strptime(user["time_goal"], "%b %d, %Y")) - time.time()) // 86400)
    weeks_until_goal = days_until_goal // 7
    hours_left = int(user["goal"]) - total_hours
    hours_per_week = round(hours_left / weeks_until_goal, 2)
    return {"total_info": total_info, "night_info": night_info, "total_percent": total_percent,
            "night_percent": night_percent, "days_until_goal": str(days_until_goal) + " Days",
            "hours_per_week": str(hours_per_week) + " Hours"}
