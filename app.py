from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
from bs4 import BeautifulSoup
app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.6pe7g.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghaemusic99
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
from datetime import datetime, timedelta
# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    # 쿠키에 저장된 토큰 값 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 가져온 토큰 값을 디코드 해준 후 유저 정보 (아이디) 사용
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']})
        return render_template('index.html', nickname=user_info["nickname"], id = user_info["username"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/detail/<id>')
def detail(id):
    # 쿠키에 저장된 토큰 값 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 가져온 토큰 값을 디코드 해준 후 유저 정보 (아이디) 사용
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']})

        return render_template('detail.html', id = id, username=user_info["username"], nickname=user_info["nickname"])

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/music', methods=['GET'])
def music_get():
    music_list = list(db.music_list.find({}, {'_id': False}))
    liked = list(db.liked.find({}, {'_id': False}))
    return jsonify({'music': music_list, 'liked': liked})

@app.route('/review', methods=['GET'])
def review_get():
    songid_receive = request.args.get('songid')
    review_list = list(db.review_list.find({'songid':songid_receive}, {'_id': False}))
    return jsonify({'review_list': review_list})

@app.route("/review/add", methods=["POST"])
def review_add():
    songid_receive = request.form['songid_give']
    nickname_receive = request.form['nickname_give']
    comment_receive = request.form['comment_give']

    doc = {'songid': songid_receive, 'nickname': nickname_receive, 'comment': comment_receive}
    db.review_list.insert_one(doc)

    return jsonify({'msg':'리뷰가 등록되었습니다.'})

#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    nickname_receive = request.form['nickname_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "nickname": nickname_receive                               # 닉네임
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/liked/plus', methods=['POST'])
def plusLiked():
    songid = request.form['songid']
    username = request.form['username']
    liked = db.liked.find_one({'songid': songid})
    liked_users = liked['user_list']
    liked_count = liked['count']
    liked_count += 1
    liked_users.append(username)
    db.liked.update_one({'songid': songid}, {'$set': {'user_list': liked_users}})
    db.liked.update_one({'songid': songid}, {'$set': {'count': liked_count}})

    return jsonify({'result': 'success'})

@app.route('/liked/minus', methods=['POST'])
def minusLiked():
    songid = request.form['songid']
    username = request.form['username']
    liked = db.liked.find_one({'songid': songid})
    liked_users = liked['user_list']
    liked_count = liked['count']
    liked_count -= 1
    liked_users.remove(username)
    db.liked.update_one({'songid': songid}, {'$set': {'user_list': liked_users}})
    db.liked.update_one({'songid': songid}, {'$set': {'count': liked_count}})

    return jsonify({'result': 'success'})

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route("/musicdetail", methods=["GET"])
def select_music_detail():
    id = request.args.get('id')
    data = requests.get('https://www.melon.com/song/detail.htm?songId='+id, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    image = soup.select_one('#downloadfrm > div > div > div.thumb > a > img')['src']
    album = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(2) > a').text
    date = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(4)').text
    lyric = soup.select_one('#d_video_summary').text
    music = db.music_list.find_one({'id':id}, {'_id': False})
    return jsonify({'music': music, 'image': image, 'album': album, 'date': date, 'lyric': lyric})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
