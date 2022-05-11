from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import certifi
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import music_update
ca = certifi.where()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'
client = MongoClient('mongodb+srv://test:sparta@cluster0.zgm92.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghae_music99

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/music_list')
def get_musicList():
    token_receive = request.cookies.get('mytoken')
    try:

        musics = list(db.musics.find({}, {'_id': False}).limit(99))
        return jsonify({"result": "success", "musics": musics})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/login')
def login():

    return render_template('login.html')

@app.route('/register')
def register():

    return render_template('register.html')

@app.route('/detail/<number>')
def detail(number):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        music = list(db.musics.find({'number':number}, {'_id': False}))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        url = "https://www.melon.com/song/detail.htm?songId=" + number
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        # downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(4)
        # downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)
        date = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(4)').text
        genre = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)').text
        video = "https://www.youtube.com/results?search_query="+music[0]['title']
        user_info = db.users.find_one({"userId": payload["id"]})
        count_heart = db.likes.count_documents({"title": music[0]['title']})
        heart_by_me = bool(db.likes.find_one({"title": music[0]['title'], "userId": payload['id']}))
        data= {
            "userId": user_info["userId"],
            'title': music[0]['title'],
            'image': music[0]['image'],
            'album': music[0]['album'],
            'artist': music[0]['artist'],
            'date': date,
            'genre': genre,
            'video': video,
            "count_heart": count_heart,
            "heart_by_me": heart_by_me
        }

        return render_template('detail.html', data=data, number=number)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/user/<userId>')
def user(userId):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (userId == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        user_info = db.users.find_one({"userId": userId}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/user/<userId>/likeMusic')
def get_likeMusic(userId):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": userId}, {"_id": False})
        all_likes = list(db.likes.find({'userId': user_info['userId']}, {'_id': False}))
        all_music=[]
        for like in all_likes:
            musics = list(db.musics.find({'title': like['title']}, {'_id': False}))
            count_heart = db.likes.count_documents({"title": like['title']})
            heart_by_me = bool(db.likes.find_one({"title": like['title'], "userId": payload['id']}))
            musics.append(count_heart)
            musics.append(heart_by_me)
            all_music.append(musics)
        return jsonify({"result": "success", "musics": all_music})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    userId_receive = request.form['userId_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'userId': userId_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': userId_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    userId_receive = request.form['userId_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "userId": userId_receive,                                   # 아이디
        "username": username_receive,                               # 이름
        "password": password_hash,                                  # 비밀번호
                                                                    # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userId_receive = request.form['userId_give']
    exists = bool(db.users.find_one({"userId": userId_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 프로필 업데이트
        userId = payload['id']
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "username": name_receive,
            "profile_info": about_receive
        }
        if 'pic_give' in request.files:
            file = request.files["pic_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"/{userId}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'userId': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/comments', methods=['POST'])
def comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        title_receive = request.form['title_give']
        num = len(list(db.comments.find({'title':title_receive},{'_id':False})))
        doc = {
            "title": title_receive,
            "userId": user_info["userId"],
            "username": user_info["username"],
            "userpic": user_info['profile_pic_real'],
            "comment": comment_receive,
            "date": date_receive,
            "num": num+1
        }
        db.comments.insert_one(doc)
        return jsonify({"result": "success", 'msg': '등록 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route("/get_comments", methods=['GET'])
def get_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]}, {'_id': False})
        title_receive = request.args.get('title_give')
        comments = list(db.comments.find({'title': title_receive}).sort("date", -1).limit(20))
        userInfo={
            'userId': user_info['userId'],
            'profile_pic': user_info['profile_pic_real']
        }
        for comment in comments:
            comment["_id"] = str(comment["_id"])
        return jsonify({"result": "success", "comments": comments, "userInfo": userInfo})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/comments/update', methods=['POST'])
def update_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        comment_receive = request.form["comment_give"]
        title_receive = request.form['title_give']
        date_receive = request.form['date_give']
        num_receive = request.form['num_give']

        print(type (num_receive))
        db.comments.update_one({'title': title_receive, 'num': int(num_receive)}, {'$set': {'comment': comment_receive, 'date': date_receive}})
        return jsonify({"result": "success", 'msg': '수정 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/comments/delete', methods=['POST'])
def delete_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        title_receive = request.form['title_give']
        num_receive = request.form['num_give']

        print(num_receive)
        db.comments.delete_one({'title': title_receive, 'num': int(num_receive)})
        return jsonify({"result": "success", 'msg': '삭제 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        title_receive = request.form["title_give"]
        action_receive = request.form["action_give"]
        doc = {
            "title": title_receive,
            "userId": user_info["userId"],
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"title": title_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route("/schedule")
def trigger():
    return music_update.music_update()

#apscheduler 선언
sched = BackgroundScheduler(daemon=True)

#apscheduler실행설정, 6시간마다 반복실행
sched.add_job(trigger, 'interval', hours=6)

#apscheduler실행설정, Cron방식으로, 1주-53주간실행, 월요일부터일요일까지실행, 21시에실행
# sched.add_job(trigger,'cron', week='1-53', day_of_week='0-6', hour='21')

#apscheduler실행
sched.start()

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
