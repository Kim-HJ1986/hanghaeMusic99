from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.6pe7g.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghaemusic99

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
all_musics = list(db.music_list.find({}, {'_id': False}))

for music in all_musics:
    songid = music['id']
    count = 0
    user_list = []

    doc = {
        'songid': songid,
        'count': count,
        'user_list': user_list
    }

    db.liked.insert_one(doc)