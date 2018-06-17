from pymongo import MongoClient

from tools import config, user_check, time_manage

credentials = config.CredentialsManager()
client = MongoClient(credentials.get_mongo_credentials())
db = client.drivelog
users = db.users


def get(username, value):
    return users.find_one({"username": username})[value]


def get_drive_list(username):
    if user_check.check_username(username):
        return users.find_one({"username": username})["drives"]
    else:
        return []


def get_drive_data(username):
    if user_check.check_username(username):
        drive_list = get_drive_list(username)
        drive_data = []
        for drive in drive_list:
            start_date = time_manage.iso_utc_to_date(username, drive["startTime"])
            start_time = time_manage.iso_utc_to_time(username, drive["startTime"])
            stop_time = time_manage.iso_utc_to_time(username, drive["stopTime"])
            duration = time_manage.drive_duration_formatted(drive["startTime"], drive["stopTime"])
            drive_data.append(
                {"startDate": start_date, "startTime": start_time, "stopTime": stop_time, "duration": duration,
                 "id": drive_list.index(drive), "conditions": drive["conditions"]})
        return drive_data


def get_drive(username, drive_id):
    if user_check.check_username(username):
        drive = get(username, "drives")[int(drive_id)]
        start_date = time_manage.iso_utc_to_date(username, drive["startTime"])
        start_time = time_manage.iso_utc_to_time(username, drive["startTime"])
        stop_time = time_manage.iso_utc_to_time(username, drive["stopTime"])
        duration = time_manage.drive_duration_formatted(drive["startTime"], drive["stopTime"])
        return {"startDate": start_date, "startTime": start_time, "stopTime": stop_time, "duration": duration,
                "id": get_drive_list(username).index(drive), "conditions": drive["conditions"]}


def get_active_drive(username):
    if user_check.check_username(username):
        for drive in users.find_one({"username": username})["drives"]:
            if drive["active"]:
                return drive
        return


def get_stats(username):
    user = users.find_one({"username": username})
    total_time = 0
    night_time = 0
    for drive in user["drives"]:
        if not drive["active"]:
            total_time += time_manage.drive_duration_seconds(drive["startTime"], drive["stopTime"])
            if "night" in drive["conditions"]:
                night_time += time_manage.drive_duration_seconds(drive["startTime"], drive["stopTime"])
    total_hours = round(total_time // 3600)
    total_minutes = round((total_time % 3600) / 60)
    total_info = f"{total_hours} hours {total_minutes} minutes"
    night_hours = round(night_time // 3600)
    night_minutes = round((night_time % 3600) / 60)
    night_info = f"{night_hours} hours {night_minutes} minutes"
    total_percent = str(round(((total_time / 3600) / int(user["goal"])) * 100)) + "%"
    night_percent = str(round(((night_time / 3600) / int(user["goal"])) * 100)) + "%"
    days_until_goal = time_manage.days_until_goal(username)
    if days_until_goal > 0:
        weeks_until_goal = days_until_goal // 7
        hours_left = int(user["goal"]) - total_hours
        hours_per_week = round(hours_left / weeks_until_goal, 2)
    else:
        hours_per_week = "0"
    return {"total_info": total_info, "night_info": night_info, "total_percent": total_percent,
            "night_percent": night_percent, "days_until_goal": str(days_until_goal) + " Days",
            "hours_per_week": str(hours_per_week) + " Hours"}


def get_start_time(username):
    if user_check.check_username(username) and get(username, "activeDrive"):
        return get_active_drive(username)["startTime"]
    else:
        return time_manage.unix_now()


def get_settings_prefill(username):
    return {"date_goal": time_manage.iso_utc_to_date(username, get(username, "date_goal")),
            "goal": get(username, "goal"),
            "night_goal": get(username, "night_goal")}


def get_change_password_error_link(username, token, error):
    return f"/change_password/{username}/{token}?error={error}"
