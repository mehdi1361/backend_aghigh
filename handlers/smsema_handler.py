import requests
import json


class SmsemaHandler:

    username = None
    password = None
    sender_number = None
    api_url = "http://37.130.202.188/services.jspd"

    def __init__(self, config):

        self.username = config["username"]
        self.password = config["password"]
        self.sender_number = config["sender_number"]

        if "api_url" in config:
            self.api_url = config["api_url"]

    def check_credit(self):

        post_params = {
            "uname": self.username,
            "pass": self.password,
            "op": "credit"
        }

        credit_check_resp = requests.post(url=self.api_url, data=post_params)

        try:
            resp = credit_check_resp.json()

            res_code = resp[0]
            res_data = resp[1]

            return res_code, res_data

        except ValueError:

            return 0, []

    def send_sms(self, message, to):

        receiver_list = to
        if not isinstance(to, list):

            receiver_list = [to]

        post_params = {
            "uname": self.username,
            "pass": self.password,
            "from": self.sender_number,
            "message": message,
            "to": json.dumps(receiver_list),
            "op": "send"
        }

        send_sms_resp = requests.post(url=self.api_url, data=post_params)

        try:
            resp = send_sms_resp.json()

            res_code = resp[0]
            res_data = resp[1]

            return res_code, res_data

        except ValueError:

            return 0, []
