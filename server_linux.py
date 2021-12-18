import re
import yaml

from flask import Flask, request
app = Flask(__name__)

from regex import *
from utils import Log, db_retry_until_unlocked
from ORM import SQL 

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
LOGFILE = DIRECTION + CONFIG['server_linux_logfile']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
db = SQL(QUEUE_DIR)
l = Log(LOGFILE)
#================================================================

def extract_link(raw: bytes) -> str:
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", raw)
    return matches.group(0).strip()

def extract_channel_name(raw: bytes) -> str:
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<\name\>).+(?=\</\name\>)", raw)
    return matches.group(0).strip()
      

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        if request.args.get('hub.challenge', ''):
            return request.args.get('hub.challenge', '')

    elif request.method == 'POST':
        l.log(LOGFILE, f"Incoming webhook with following data: {request.data}")
        link = extract_link(request.data)

        db.push_to_queue(link)
        
        l.log(LOGFILE, f"Link \"{link}\" from {extract_link} inserted!")
        return '200'

if __name__=='__main__':
    db.create_table()
    app.run()
