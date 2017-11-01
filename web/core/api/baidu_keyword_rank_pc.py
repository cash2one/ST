import requests
import logging
from yhklibs import yhk_app

URL = 'http://apis.5118.com/keywordrank/baidupc'

logger = logging.getLogger(__name__)


def create_task(keyword, num):
    data = {"keywords": keyword, "checkrow": num}
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"APIKEY {yhk_app.config['API_KEY_BAIDU_KEYWORD_RANK_PC']}"}
    r = requests.post(URL, data=data, headers=headers)
    r = r.json()
    code = int(r.get("errcode"))
    if code == 0:
        taskid = r["data"]["taskid"]
        return taskid, {"code": code, "message": "success"}, code
    else:
        logger.error(f'{code}:{r.get("errmsg")}')
        return None, r, code


def get_task_data(taskid):
    data = {"taskid": taskid}
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"APIKEY {yhk_app.config['API_KEY_BAIDU_KEYWORD_RANK_PC']}"}
    r = requests.post(URL, data=data, headers=headers)
    r = r.json()
    code = int(r.get("errcode"))
    if code == 0:
        keyword_monitor = r["data"]["keyword_monitor"]
        result = []
        for key in keyword_monitor:
            keyword = key["keyword"]
            ranks = key["ranks"]
            for rank in ranks:
                rank.update({"keyword": keyword})
                result.append(rank)
        return result, {"code": code, "message": "success"}, code
    else:
        logger.error(f'{code}:{r.get("errmsg")}')
        return [], r, code
