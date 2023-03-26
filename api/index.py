import requests
from flask import Flask, jsonify, send_file
from io import BytesIO

app = Flask(__name__)


@app.route('/api/v1/bangumi/<int:mid>', methods=['GET'])
def bangumi(mid: int):
    bangumi_list = []

    page = 1
    while True:
        r = requests.get(
            'https://api.bilibili.com/x/space/bangumi/follow/list', params={
                'type': 1,
                'vmid': mid,
                'pn': page,
                'ps': 30,
            }
        )
        if not r.json()['data']['list']:
            break

        for bangumi in r.json()['data']['list']:
            bangumi_list.append({
                'title': bangumi['title'],
                'url': bangumi['url'],
                'cover': f"https://mirai-api.vercel.app/proxy/cover/{bangumi['cover'].split('/')[-1]}",
                'total_count': bangumi['total_count'],
                'areas': bangumi['areas'][0]['name'],
                'desc': bangumi['summary'],
                'coin': bangumi['stat']['coin'],
                'danmaku': bangumi['stat']['danmaku'],
                'view': bangumi['stat']['view'],
                'series_follow': bangumi['stat']['series_follow'],
            })

        page += 1

    return jsonify(bangumi_list)


@app.route('/proxy/cover/<string:id>')
def cover(id: str):
    mime_type = ''
    if id.endswith('.jpg') or id.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif id.endswith('.png'):
        mime_type = 'image/png'
        id = f'/image/{id}'

    r = requests.get(f'http://i0.hdslb.com/bfs/bangumi/{id}', stream=True)

    return send_file(BytesIO(r.content), mimetype=mime_type)
