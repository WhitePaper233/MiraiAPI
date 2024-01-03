from io import BytesIO

import requests
from flask import Flask, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 查询用户番剧数据
@app.route('/api/v1/bangumi/<int:mid>', methods=['GET'])
def bangumi(mid: int):
    bangumi_list = []
    page = 1
    headers = {"User_Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    while True:
        r = requests.get(
            'https://api.bilibili.com/x/space/bangumi/follow/list', params={
                'type': 1,
                'vmid': mid,
                'pn': page,
                'ps': 30,
            },
            headers = headers
        )
        resp_data = r.json()
        if resp_data['code']:
            return jsonify({'code': resp_data['code']}), r.status_code
        if not resp_data['data']['list']:
            break
        for bangumi in resp_data['data']['list']:
            try:
                bangumi_list.append({
                    'season_id': bangumi['season_id'],
                    'follow_status': bangumi['follow_status'],
                    'title': bangumi['title'],
                    'url': bangumi['url'],
                    'cover': bangumi['cover'],
                    'total_count': bangumi['total_count'],
                    'areas': bangumi['areas'][0]['name'],
                    'desc': bangumi['summary'],
                    'coin': bangumi['stat']['coin'],
                    'danmaku': bangumi['stat']['danmaku'],
                    'view': bangumi['stat']['view'],
                    'score': str(bangumi['rating']['score']),
                    'series_follow': bangumi['stat']['series_follow'],
                })
            except KeyError:
                bangumi_list.append({
                    'season_id': bangumi['season_id'],
                    'follow_status': bangumi['follow_status'],
                    'title': bangumi['title'],
                    'url': bangumi['url'],
                    'cover': bangumi['cover'],
                    'total_count': bangumi['total_count'],
                    'areas': bangumi['areas'][0]['name'],
                    'desc': bangumi['summary'],
                    'coin': bangumi['stat']['coin'],
                    'danmaku': bangumi['stat']['danmaku'],
                    'view': bangumi['stat']['view'],
                    'score': '',
                    'series_follow': bangumi['stat']['series_follow'],
                })
        page += 1
    resp = jsonify({'code': 0, 'data': bangumi_list})
    return resp, r.status_code


# 图片防盗链代理
@app.route('/proxy/bangumi/cover/<string:id>')
def cover(id: str):
    mime_type = ''
    if id.endswith('.jpg') or id.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif id.endswith('.png'):
        mime_type = 'image/png'
        id = f'/image/{id}'
    r = requests.get(f'http://i0.hdslb.com/bfs/bangumi/{id}', stream=True)
    if r.status_code != 200:
        return None, r.status_code
    resp = send_file(BytesIO(r.content), mimetype=mime_type)
    return resp, r.status_code
