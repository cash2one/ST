import requests
import base64
from yhklibs import yhk_app

SMS_TXT_CODE_URL = 'https://api.sms.jpush.cn/v1/codes'
SMS_TXT_CODE_VALID_URL = 'https://api.sms.jpush.cn/v1/codes/%s/valid'


class Jpush(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Jpush, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
            cls._instance.app_key = yhk_app.config["APP_KEY"]
            cls._instance.master_secret = yhk_app.config["MASTER_SECRET"]
            cls._instance.base64_auth_string = base64.b64encode(
                f'{cls._instance.app_key}:{cls._instance.master_secret}'.encode("utf-8")).decode(
                "utf-8")
            cls._instance.headers = {"Content-Type": "application/json",
                                     "Authorization": f"Basic {cls._instance.base64_auth_string}"}
        return cls._instance

    def send_sms_txt_codes(self, mobile, temp_id=1):
        try:
            data = {"mobile": mobile, "temp_id": temp_id}
            r = requests.post(SMS_TXT_CODE_URL, json=data, headers=self.headers)
            r = r.json()
            error = r.get("error")
            if error:
                print(error)
                return None
            # {"msg_id":"354838553987"}
            return r.get("msg_id")
        except Exception as e:
            print(e)
            return None

    def valid_sms_txt_codes(self, msg_id, code):
        try:
            data = {"code": code}
            url = SMS_TXT_CODE_VALID_URL % msg_id
            r = requests.post(url, json=data, headers=self.headers)
            r = r.json()
            is_valid = r.get("is_valid")
            if not is_valid:
                print(r.get("error"))
                return False
            return True
        except Exception as e:
            print(e)
            return False

# result = Jpush().valid_sms_txt_codes("354838553987", "029789")
# print(result)
