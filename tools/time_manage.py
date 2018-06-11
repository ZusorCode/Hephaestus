import datetime
import pytz
from dateutil import parser
from pymongo import MongoClient
from tools import config, user_check, user_get
credentials = config.CredentialsManager()
client = MongoClient(credentials.get_mongo_credentials())
db = client.drivelog
users = db.users


def iso_utc_to_date(username, iso_utc):
    if user_check.check_username(username):
        date_object = parser.parse(iso_utc)
        timezone = user_get.get(username, "timezone")
        localized_time = date_object.astimezone(pytz.timezone(timezone))
        return datetime.datetime.strftime(localized_time, "%b %d, %Y")
    else:
        return "Error"


def iso_utc_to_time(username, iso_utc):
    if user_check.check_username(username):
        date_object = parser.parse(iso_utc)
        timezone = user_get.get(username, "timezone")
        localized_time = date_object.astimezone(pytz.timezone(timezone))
        return datetime.datetime.strftime(localized_time, "%I:%M %p")
    else:
        return "Error"


def iso_utc_to_local(username, iso_utc):
    if user_check.check_username(username):
        date_object = parser.parse(iso_utc)
        timezone = user_get.get(username, "timezone")
        localized_time = date_object.astimezone(pytz.timezone(timezone))
        return localized_time.isoformat()


def date_local_to_iso_utc(username, date_local):
    if user_check.check_username(username):
        timezone = user_get.get(username, "timezone")
        user_timezone = pytz.timezone(user_get.get(username, "timezone"))
        datetime_local = datetime.datetime.strptime(date_local, "%b %d, %Y")
        datetime_local = datetime_local.replace(tzinfo=user_timezone)
        return datetime_local


# TODO: Find better function name
def update_drive_thing(username, date, start_time, stop_time):

def drive_duration_formatted(start_time, stop_time):
    start_datetime = parser.parse(start_time)
    stop_datetime = parser.parse(stop_time)
    difference = stop_datetime - start_datetime
    hours, remainder = divmod(difference.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours < 10:
        hours = f"0{str(int(hours))}"
    else:
        hours = str(int(hours))
    if minutes < 10:
        minutes = f"0{str(int(minutes))}"
    else:
        minutes = str(int(minutes))
    return f"{hours}:{minutes}"


def drive_duration_seconds(start_time, stop_time):
    start_datetime = parser.parse(start_time)
    stop_datetime = parser.parse(stop_time)
    difference = stop_datetime - start_datetime
    return difference.total_seconds()


def days_until_goal(username):
    goal = user_get.get(username, "date_goal")
    difference = parser.parse(goal) - datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    if difference >= 0:
        difference = difference.days
        difference = f"{str(difference)} Days"
    else:
        difference = "No more days"
    return difference


def iso_utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


print(date_local_to_iso_utc("Zusor", "Jun 06, 2018"))
