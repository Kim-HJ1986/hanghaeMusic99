import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi

import schedule
import time

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.6pe7g.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghaemusic99

#마치 사람이 요청을 날린 것 처럼 보여주기 위해 사용, 브라우저에서 요청한 것처럼됨. (실제론 코드에서 날림)
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

def insertMusic():
    data = requests.get('https://www.melon.com/chart/',headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    musics_50 = soup.select('#lst50')
    musics_100 = soup.select('#lst100')
    all_musics = musics_50 + musics_100

    #print(all_musics)
    #lst50
    #lst50 > td:nth-child(8) > div > button
    for music in all_musics:
        id = music.attrs
        id = id['data-song-no']
        rank = music.select_one('td:nth-child(2) > div > span.rank ').text
        title = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a').text
        singer = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank02 > a').text
        image_url = music.select_one('td:nth-child(4) > div > a > img')['src']

        doc = {
            'id': id,
            'rank': rank,
            'title': title,
            'singer': singer,
            'image_url': image_url
        }

        #db.music_list.insert_one(doc)

def insertDBTest():
    # doc={
    #     'test': "테스트입니다."
    # }
    # db.schedule.insert_one(doc)
    print("스케쥴테스트")

schedule.every(3).seconds.do(insertDBTest) # 15초마다 insertMusic 실행

def triggerHere():
    while True:
        schedule.run_pending()
        time.sleep(1)
