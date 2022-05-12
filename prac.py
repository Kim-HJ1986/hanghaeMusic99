from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
import certifi
import requests
from bs4 import BeautifulSoup
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.zgm92.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.hanghae_music99
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.melon.com/chart/index.htm',headers=headers)
# data = requests.get('https://www.melon.com/song/detail.htm?songId=34997078',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')
#lst50 > td:nth-child(4) > div > a > img
#lst50 > td:nth-child(4) > div > a > img
#lst50 > td:nth-child(4) > div > a > img

#lst100 > td:nth-child(4) > div > a > img

#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a
#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank02 > a
#lst50 > td:nth-child(7) > div > div > div > a

#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a
#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank02 > a
#lst50 > td:nth-child(7) > div > div > div > a

#lst50 > td:nth-child(4) > div > a

#lst50 > td:nth-child(2) > div > span.rank

music1 = soup.select('#lst50')
music2 = soup.select('#lst100')
musics=music1+music2


#lst50 > td:nth-child(5) > div > a
for music in musics:
    title = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a').text
    artist = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank02 > a').text
    image1 = music.select_one('td:nth-child(4) > div > a > img')['src']
    album = music.select_one('td:nth-child(7) > div > div > div > a').text
    image = image1.replace('120/','300/')
    number = music.select_one('td:nth-child(5) > div > a')['href'].split("'")[1]
    rank = music.select_one('td:nth-child(2) > div > span.rank').text
    print(image)

    doc ={
        'title' : title,
        'artist' : artist,
        'image' : image,
        'album' : album,
        'number' : number,
        'rank':rank
    }

    db.musics.insert_one(doc)