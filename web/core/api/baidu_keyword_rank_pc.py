import requests
import logging

URL = 'http://apis.5118.com/keywordrank/baidupc'

logger = logging.getLogger(__name__)


def create_task(keyword, num):
    data = {"keywords": keyword, "checkrow": num}
    r = requests.post(URL, data=data, headers=headers)
    r = r.json()
    code = r.get("errcode")
    if code == '0':
        taskid = r["data"]["taskid"]
        return taskid, r
    else:
        logger.error(code + ":" + r.get("errmsg"))
        return None, r


def get_task_data(taskid):
    data = {"taskid": taskid}
    r = requests.post(URL, data=data, headers=headers)
    r = r.json()
    code = r.get("errcode")
    if code == '0':
        keyword_monitor = r["data"]["keyword_monitor"]
        result = []
        for key in keyword_monitor:
            keyword = key["keyword"]
            ranks = key["ranks"]
            for rank in ranks:
                rank.update({"keyword": keyword})
                result.append(rank)
        return result, r
    else:
        logger.error(code + ":" + r.get("errmsg"))
        return [], r, code
