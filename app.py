from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup
import billboard

from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.6pe7g.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def main():
    myname = "Sparta"
    return render_template("index.html", name=myname)


@app.route('/detail')
def detail():
    return render_template("detail.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)