from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from .base import st_web_blueprint
import requests


@st_web_blueprint.route("/index", methods=["GET", "POST"])
async def index(request):
    return html(await render_template('index.html', request=request))


@st_web_blueprint.route("/baidu/keywordrank/pc/q", methods=["POST"])
async def baidu_keywordrank_pc_task(request):
    keyword = request.form.get("keyword")
    num = request.form.get("num", 50)
    if not keyword:
        return json({"code": 500, "message": "关键词为空！"})
    result = {"code": 200}

    taskid = get_taskid(keyword, num)
    result.update({"data": {"taskid": taskid}})
    return json(result)


@st_web_blueprint.route("/baidu/keywordrank/pc/r", methods=["POST"])
async def baidu_keywordrank_pc_data(request):
    taskid = request.form.get("taskid")
    if not taskid:
        return json({"code": 500, "message": "taskid为空！"})
    r = get_task_data(taskid)
    result = {"code": 200, "data": r}
    return json(result)


def get_task_data(taskid):
    url = 'http://apis.5118.com/keywordrank/baidupc'
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": "APIKEY 288FA7C57EAB4312A96E440279DF7690"}
    data = {"taskid": taskid}
    r = requests.post(url, data=data, headers=headers)
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
        return result
    else:
        print(code + ":" + r.get("errmsg"))
        return []


def get_taskid(keyword, num):
    url = 'http://apis.5118.com/keywordrank/baidupc'
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": "APIKEY 288FA7C57EAB4312A96E440279DF7690"}
    data = {"keywords": keyword, "checkrow": num}
    r = requests.post(url, data=data, headers=headers)
    r = r.json()
    code = r.get("errcode")
    if code == '0':
        taskid = r["data"]["taskid"]
        return taskid
    else:
        print(code + ":" + r.get("errmsg"))
        return None
