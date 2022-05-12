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
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'
client = MongoClient('mongodb+srv://test:sparta@cluster0.zgm92.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghae_music99

#메인페이지
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

#db에 저장된 음악 리스트들을 가져옴(99개까지)
@app.route('/music_list')
def get_musicList():

    musics = list(db.musics.find({}, {'_id': False}).limit(99))

    return jsonify({"result": "success", "musics": musics})


#로그인 페이지
@app.route('/login')
def login():

    return render_template('login.html')

#회원가입 페이지
@app.route('/register')
def register():

    return render_template('register.html')

#음악 디테일페이지 number는 그 선택한 음악의 고유넘버입니다
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
            "username":user_info["username"],
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

#유저의 개인페이지
@app.route('/user/<userId>')
def user(userId):
    # 각 사용자의 정보와 사용자가 좋아요한 음악리스트를 볼 수있는 공간
    # 토큰을 받아옴
    token_receive = request.cookies.get('mytoken')
    # 그 토큰이 유효한지 확인
    try:
        #토큰이 유효하면 페이지를 넘어올때 받은 userId와 db에 저장된 userId를 비교하여 맞는 유저 정보를 가져와서 user.html이 실행될때 data를 넘겨줌
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": userId}, {"_id": False})
        return render_template('user.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 각 사용자가 좋아요한 음악을 가져오기
@app.route('/user/<userId>/likeMusic')
def get_likeMusic(userId):
    # 토큰을 받아옴
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰을 디코드하여 payload 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 그 페이지의 userId와 db에 저장된 userId를 비교하여 그에 맞는 유저정보를 가져옴
        user_info = db.users.find_one({"userId": userId}, {"_id": False})
        # 가져온 그 유저정보의 유저아이디와 likes라는 db에 userId를 비교하여 그 사용자가 좋아요한 음악 제목을 가져옴
        all_likes = list(db.likes.find({'userId': user_info['userId']}, {'_id': False}))
        all_music=[]
        for like in all_likes:
            # 가져온 음악 제목과 musics db에 있는 음악 제목을 비교하여 맞는 음악들을 다 가져옴
            musics = list(db.musics.find({'title': like['title']}, {'_id': False}))
            # 그 음악의 좋아요 갯수를 셈
            count_heart = db.likes.count_documents({"title": like['title']})
            # 그 음악을 내가 좋아요 했는지 확인
            heart_by_me = bool(db.likes.find_one({"title": like['title'], "userId": payload['id']}))
            # 그 정보를 music list에 담은 후 전체 리스트를 all_music에 담아줌
            musics.append(count_heart)
            musics.append(heart_by_me)
            all_music.append(musics)
        return jsonify({"result": "success", "musics": all_music})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    # 유저 아이디와 비밀번호를 받아옴
    userId_receive = request.form['userId_give']
    password_receive = request.form['password_give']
    # 비밀먼호를 hash처리 하여 저장
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 유저 아이디와 해쉬된 비밀번호를 이용하여 아이디와 비밀번호가 일치하는지 확인
    result = db.users.find_one({'userId': userId_receive, 'password': pw_hash})

    if result is not None:
        # 회원가입된 회원이라면 payload에 저장
        payload = {
         'id': userId_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # 회원에게 토큰을 할당해줌
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')  #배포환경에선 decode를 작성해줘야함
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') #로컬환경에선 decode 삭제

        return jsonify({'result': 'success', 'token': token})
        # 아이디와 비밀번호가 일치하지 않으면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입시 정보 저장
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
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "/profile_placeholder.png",             # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 회원가입이 되어있는지 체크
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userId_receive = request.form['userId_give']
    exists = bool(db.users.find_one({"userId": userId_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 개인 프로필 업데이트
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 프로필 업데이트
        userId = payload['id']
        # 업데이트한 이름과 한마디를 받아옴
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        # new_doc에 저장
        new_doc = {
            "username": name_receive,
            "profile_info": about_receive
        }
        # 보낸 파일에 사진이 있으면 실행
        if 'pic_give' in request.files:
            file = request.files["pic_give"]
            filename = secure_filename(file.filename)                    #파일 이름을 filename에 저장
            extension = filename.split(".")[-1]                          #파일 확장자를 extention에 저장 [-1]은 리스트에서 뒤에서 첫번째라는 의미(사진의 확장자를 가져와야하기때문)
            file_path = f"/{userId}.{extension}"                         #파일 경로를 새로 지정
            file.save("./static/profile_pics" + file_path)               #static/profile_pics 폴더에 파일 저장
            new_doc["profile_pic"] = filename                            #new_doc에 저장
            new_doc["profile_pic_real"] = file_path
            db.comments.update_many({'userId': payload['id']},{'$set': {'username': name_receive, 'userpic': file_path}}) # (사진있을때) 유저정보를 업데이트할때 그 전에 남긴 코멘트에도 적용해주기위해서 새로 업데이트
        db.users.update_one({'userId': payload['id']}, {'$set': new_doc})   #db에 저장된 유저정보를 업데이트
        db.comments.update_many({'userId': payload['id']},{'$set': {'username': name_receive}}) # (사진 없을때)유저정보를 업데이트할때 그 전에 남긴 코멘트에도 적용해주기위해서 새로 업데이트
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 코멘트 db에 저장
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
            "num": num+1                # num은 comment마다 번호를 주기위해서 넣었습니다
        }
        db.comments.insert_one(doc)
        return jsonify({"result": "success", 'msg': '등록 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# comment 가져오기
@app.route("/get_comments", methods=['GET'])
def get_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]}, {'_id': False})
        # 상세페이지 들어간 그 음악의 이름을 이용하여 그 음악에 달린 코멘트만 가져옴
        title_receive = request.args.get('title_give')
        comments = list(db.comments.find({'title': title_receive}, {'_id': False}).sort("date", -1).limit(20))
        # 각 사용자가 남긴 댓글에만 수정 삭제를 주기위하여 유저아이디를 넘겨줌
        userInfo={
            'username': user_info['username'],
            'userId': user_info['userId'],
            'profile_pic': user_info['profile_pic_real']
        }
        return jsonify({"result": "success", "comments": comments, "userInfo": userInfo})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 코멘트 수정
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
        db.comments.update_one({'title': title_receive, 'num': int(num_receive)}, {'$set': {'comment': comment_receive, 'date': date_receive}})
        return jsonify({"result": "success", 'msg': '수정 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 코멘트 삭제
@app.route('/comments/delete', methods=['POST'])
def delete_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userId": payload["id"]})
        title_receive = request.form['title_give']
        num_receive = request.form['num_give']
        db.comments.delete_one({'title': title_receive, 'num': int(num_receive)})
        return jsonify({"result": "success", 'msg': '삭제 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 좋아요 갯수 업데이트
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
        # action_receive를 줘서 like면 좋아요 저장하고 아니면 삭제
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        # 각 음악마다의 좋아요 갯수를 셈
        count = db.likes.count_documents({"title": title_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# 스케쥴관리 6시간마다 멜론에서 Top100을 크롤링해와서 db에 업데이트
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
