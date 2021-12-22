import re
import yaml
from bs4 import BeautifulSoup
from collections.abc import Iterable

from flask import Flask, request
app = Flask(__name__)

from utils import Log
from ORM import SQL

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
LOGFILE = DIRECTION + CONFIG['server_linux_logfile']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
db = SQL(QUEUE_DIR)
l = Log(LOGFILE)
#================================================================

def extract_by_name(content: bytes, name) -> str:
    return BeautifulSoup(content.decode('utf-8'), 'lxml').find(name).contents[0]

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        return request.args.get('hub.challenge', None)

    elif request.method == 'POST':
        data = request.data
        l.log(f"Incoming webhook with following data: {data}")
        link = extract_by_name(data, "yt:videoId")
        title = extract_by_name(data, "title")
        uploader = extract_by_name(data, "name")

        db.push_to_queue(link, title, uploader)

        l.log(f'Link "{link}" from inserted!')
        return '200'

if __name__ == '__main__':
    db.create_table()
    app.run()
