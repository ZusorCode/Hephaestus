import smtplib
from email.message import EmailMessage
from tools import user_get, config, user_manage
from os import urandom
from base64 import b64encode

credentials = config.CredentialsManager()


def send_email_confirmation(username):
    msg = EmailMessage()
    receiver = user_get.get(username, "email")
    msg["From"] = credentials.get_smtp_verify_address()
    msg["To"] = receiver
    msg["Subject"] = "Thanks for signing up!"
    random_bytes = urandom(64)
    token = b64encode(random_bytes).decode('utf-8')
    token = token.replace("+", "")
    token = token.replace("/", "")
    token = token.replace("=", "")
    verify_address = f"{credentials.get_site_url()}/verify/{username}/{token}"
    html = f"<html><head></head><body>Thanks for signing up!<br>To verify your account, click <a href=" \
           f"'{verify_address}'>here</a>.<br>Thanks!<br>If you didn't request this email you can ignore it</body></html> "
    msg.set_content(html, "html")
    server = smtplib.SMTP(credentials.get_smtp_address(), 587)
    server.starttls()
    server.login(credentials.get_smtp_username(), credentials.get_smtp_password())
    server.sendmail(credentials.get_smtp_verify_address(), receiver, msg.as_string())
    server.quit()
    user_manage.associate_token(username, token)


def send_forgot_password(username):
    msg = EmailMessage()
    receiver = user_get.get(username, "email")
    msg["From"] = credentials.get_smtp_forgot_password_address()
    msg["To"] = receiver
    msg["Subject"] = "Reset your password"
    random_bytes = urandom(64)
    token = b64encode(random_bytes).decode('utf-8')
    token = token.replace("+", "")
    token = token.replace("/", "")
    token = token.replace("=", "")
    verify_address = f"{credentials.get_site_url()}/change_password/{username}/{token}"
    html = f"<html><head></head><body>To reset your password, click <a href=" \
           f"'{verify_address}'>here</a>.<br>If you didn't request this email you can ignore it!</body></html> "
    msg.set_content(html, "html")
    server = smtplib.SMTP(credentials.get_smtp_address(), 587)
    server.starttls()
    server.login(credentials.get_smtp_username(), credentials.get_smtp_password())
    server.sendmail(credentials.get_smtp_forgot_password_address(), receiver, msg.as_string())
    server.quit()
    user_manage.associate_password_token(username, token)
