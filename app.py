from flask import Flask, redirect, session, render_template, request, url_for
from functools import wraps
from os import urandom
from tools import user_info, user_manage
from datetime import datetime, timedelta
import time
app = Flask(__name__)
app.secret_key = urandom(5000)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("route"))
        if not session["logged_in"] is True:
            return redirect(url_for("route"))
        return f(*args, **kwargs)

    return decorated_function


def no_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged_in"):
            if session["logged_in"] is True:
                return redirect(url_for("route"))
        if session.get("username"):
            if session["username"] != "":
                return redirect(url_for("route"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def route():
    if session.get("logged_in"):
        if session["logged_in"]:
            if session.get("username"):
                return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login")
@no_login
def login():
    error = request.args.get("error")
    if error:
        return render_template("Login.html", error=error)
    return render_template("Login.html")


@app.route("/do_login", methods=["GET", "POST"])
@no_login
def do_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user_info.check_password(username, password):
            session["logged_in"] = True
            session["username"] = username
        else:
            return redirect("/login?error=login")
    return redirect(url_for("route"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("route"))


@app.route("/register")
@no_login
def register():
    error = request.args.get("error")
    if error:
        return render_template("Register.html", error=error)
    return render_template("Register.html")


@app.route("/do_register", methods=["GET", "POST"])
@no_login
def do_register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password_repeat = request.form["password_repeat"]
        if user_info.check_username(username):
            return redirect("/register?error=username")
        elif user_info.check_email(email):
            return redirect("/register?error=email")
        elif not password == password_repeat:
            return redirect("/register?error=password")
        else:
            if user_manage.register(username, email, password):
                return redirect(url_for("login"))
            else:
                return "Error"


@app.route("/home")
@login_required
def home():
    error = request.args.get("error")
    return render_template("Home.html", username=session["username"],
                           running=user_info.check_drive(session["username"]),
                           startTime=user_info.get_start_time(session["username"]),
                           time_goal=user_info.get_time_goal(session["username"]),
                           goal=user_info.get_goal(session["username"]),
                           night_goal=user_info.get_night_goal(session["username"]),
                           error=error, )


@app.route("/get_table")
@login_required
def get_table():
    return render_template("Table.html", drives=user_info.get_drive_data(session["username"]))


@app.route("/get_editable_table")
@login_required
def get_editable_table():
    id = request.args.get("id")
    return render_template("EditTable.html", drive=user_info.get_drive(session["username"], id))


@app.route("/edit_data", methods=["GET", "POST"])
@login_required
def edit_data():
    start_date = request.form["startDate"]
    start_time = request.form["startTime"]
    stop_time = request.form["stopTime"]
    id = request.form["id"]
    start_timestamp = datetime.strptime(f"{start_date} {start_time}", "%b %m, %Y %I:%M %p").timestamp()
    stop_timestamp = datetime.strptime(f"{start_date} {stop_time}", "%b %m, %Y %I:%M %p").timestamp()
    if start_timestamp > stop_timestamp:
        stop_timestamp += timedelta(days=1)
    user_manage.update_drive(session["username"], id, start_timestamp, stop_timestamp)


@app.route("/start_drive", methods=["GET", "POST"])
@login_required
def start_drive():
    if request.method == "POST":
        username = request.form["username"]
        if username == session["username"]:
            if not user_info.check_drive(username):
                return str(user_manage.start_drive(username))


@app.route("/stop_drive", methods=["GET", "POST"])
@login_required
def stop_drive():
    if request.method == "POST":
        username = request.form["username"]
        if username == session["username"]:
            if user_info.check_drive(username):
                return str(user_manage.stop_drive(username))


@app.route("/delete_drive", methods=["GET", "POST"])
@login_required
def delete_drive():
    user_manage.remove_drive(session["username"], request.form["id"])
    return "True"


@app.route("/change_settings", methods=["GET", "POST"])
@login_required
def change_settings():
    if request.method == "POST":
        time_goal = request.form["time_goal"]
        goal = request.form["goal"]
        night_goal = request.form["night_goal"]
        if time_goal == "":
            return redirect("/home?error=missing#settings")
        if goal == "":
            return redirect("/home?error=missing#settings")
        if night_goal == "":
            return redirect("/home?error=missing#settings")
        if user_manage.update_settings(session["username"], time_goal, goal, night_goal):
            return redirect("/home?error=settings_change_success#settings")
        else:
            return redirect("/home?error=settings_change_error#settings")


@app.route("/login_check")
def login_check():
    if not session.get("logged_in"):
        return "false"
    elif not session["logged_in"] is True:
        return "false"
    elif not session.get("username"):
        return "false"
    else:
        return "true"


if __name__ == '__main__':
    app.run()
