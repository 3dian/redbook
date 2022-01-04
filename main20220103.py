# -*- coding:utf-8 -*-

# 用户Sessionid = 1616761780919058355044 不变

# 爬取小红书相关信息

import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import hashlib
import urllib

# 测试数据:

test_user_id = 'http://10.203.26.118:8001/base_info/5ef951a000000000010078d2'
test_note_id = 'http://10.203.26.118:8001/note_info/60bae5ae0000000001029b28'
test_note_list_id = 'http://10.203.26.118:8001/user_note/5ef951a000000000010078d2'
test_user_note = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/5ef951a000000000010078d2/notes?page=1&page_size=15'

############ 小红书笔记信息获取 核心代码 ##################################

# 笔记的请求头 拼接x-sign字段

headers_xiao_hong_shu_note = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
    "accept-language": 'zh-CN,zh;q=0.9,ko;q=0.8,en;q=0.7',
    'Authorization': 'wxmp.ba6d4702-ca72-4b2e-a1a3-8b396fc63c8e',
}

# 添加user请求头

headers_user = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
    "accept-language": 'zh-CN,zh;q=0.9,ko;q=0.8,en;q=0.7',
    "Authorization": 'wxmp.ba6d4702-ca72-4b2e-a1a3-8b396fc63c8e',
}


def get_xsign_notelist(user_id):
    data = f"/fe_api/burdock/weixin/v2/user/{user_id}/notes?page=1&page_size=15WSUDD"
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return "X" + sign


def get_xsign_user(user_id):
    data = f"/fe_api/burdock/weixin/v2/user/{user_id}WSUDD"
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return "X" + sign


def get_xsign_note(item_id):
    """
    获取笔记id的x-sign
    :param item_id:
    :return:
    """
    url_ = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/' + \
        str(item_id)
    data = url_[27:] + "WSUDD"
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return "X" + sign


################################End######################################

######################非核心模块########################

# 全局变量使用大写，其余全部小写

SLICE_URL = "https://www.xiaohongshu.com/user/profile/"

# 如果测试失败的话 需要更新cookie 即更改G_RED_BOOK_COOKIE 即可

G_RED_BOOK_COOKIE = "kong_html_injector=1613982768; kong_path_inject=/user/profile/5c908e080000000012004390; xhsTrackerId=6c386e29-cd41-47ae-c700-5d74f13b3f09; xhsuid=bMo3QFwbfPV4WChs; timestamp2=20210529952d9f7c12ac396212e02216; timestamp2.sig=6n3DRvj4YMS5hupgwlfaztbElBWMSzDIpNHsiJow0SY; lang=en-US; smidV2=2021052913550488075f3e9f1c752d70bc958ae0f9c1bb0043cedad1f8eb540; extra_exp_ids=gif_clt1,ques_exp1"
g_cookies = dict(map(lambda x: x.split('='), G_RED_BOOK_COOKIE.split(";")))

# g_rtn_json 用于记录获取的数据

g_rtn_json = {
}


def py_note_url(url):
    """
    爬取笔记相关的信息
    :param url:
    :return:
    """
    res = requests.get(url, headers=headers_xiao_hong_shu_note)
    res.encoding = 'utf-8'
    str_json = json.loads(res.content)
    str_likes = str_json['data']['likes']  # 赞
    str_comments = str_json['data']['comments']  # 评论
    str_share_count = str_json['data']['shareCount']  # 转发
    str_collect = str_json['data']['collects']  # 收藏
    print(str_json['data']['user']['nickname'])
    rtn_json = {
        'likes': str_likes,  # 赞
        'comments': str_comments,  # 评论
        'shareCount': str_share_count,  # 转发
        'collects': str_collect,  # 收藏
        'title': str_json['data']['title'],  # 标题
        'desc': str_json['data']['desc'],  # 描述
        'time': str_json['data']['time'],
        'nickname': str_json['data']['user']['nickname'],
        'image': str_json['data']['user']['image']
    }
    print(rtn_json)
    return rtn_json


####################Flask请求封装开始################################################

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'HelloWorld'


@app.route('/user_note/<uid>')
def get_user_note(uid):
    """
    获取用户笔记list信息
    :param uid:
    :return:
    """
    x_sign = get_xsign_notelist(uid)
    print(x_sign)
    headers_user['x-sign'] = x_sign
    res = requests.get('https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/' +
                       uid+'/notes?page=1&page_size=15', headers=headers_user)
    res.encoding = 'utf-8'
    return res.content


@app.route('/base_info/<uid>')
def get_base_info(uid):
    """
    获取相关信息
    :param uid:
    :return:
    """
    x_sign = get_xsign_user(uid)
    print(x_sign)
    headers_user['x-sign'] = x_sign
    res = requests.get('https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/' +
                       uid, headers=headers_user)
    res.encoding = 'utf-8'
    return res.content


@app.route('/item_link/<key>')
def get_item_url(key):
    """
    获取item_url
    :param item_url:
    :return:
    """
    item_url = "http://xhslink.com/" + key
    res = requests.get(item_url, allow_redirects=True)
    url_ = urllib.parse.unquote(res.url)
    sp = url_.split("redirectPath=")
    res_p = sp[1]
    return res_p


@app.route('/note_info/<uuid>')
def get_note_info(uuid):
    """
    :param uuid:
    :return:
    """
    note_url = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/" + \
        str(uuid)
    x_sign_note = get_xsign_note(uuid)  # 获取x_sign_note = 值
    print(x_sign_note)
    headers_xiao_hong_shu_note['x-sign'] = x_sign_note
    rtn_json = py_note_url(note_url)
    return rtn_json


#####################Flask请求结束###################################################

# end

if __name__ == '__main__':
    app.run('0.0.0.0', port=8001)
