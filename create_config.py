import os
if "config.py" not in os.listdir("tools"):
    with open("tools/config.py", "w+") as config:
        config.write("""

class CredentialsManager:
    def __init__(self):
        self.site_url = "http://example.com"
        self.mongo_credentials = "mongodb://localhost/drivelog"
        self.smtp_username = "example_user"
        self.smtp_password = "example_password"
        self.smtp_address = "smtp.example.com"
        self.smtp_verify_address = "verify@example.com"
        self.smtp_forgot_password_address = "password@example.com"

    def get_site_url(self):
        return self.site_url

    def get_mongo_credentials(self):
        return self.mongo_credentials

    def get_smtp_username(self):
        return self.smtp_username

    def get_smtp_password(self):
        return self.smtp_password

    def get_smtp_address(self):
        return self.smtp_address

    def get_smtp_verify_address(self):
        return self.smtp_verify_address

    def get_smtp_forgot_password_address(self):
        return self.smtp_forgot_password_address
    
""")
