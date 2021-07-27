import re
import sqlite3
import yaml

from flask import Flask, request

from regex import *
from utils import _log, db_retry_until_unlocked

app = Flask(__name__)

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
LOGFILE = DIRECTION + CONFIG['server_linux_logfile']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
#================================================================

def extract_link(raw):
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", raw)
    link = matches.group(0).strip()
    return link

def extract_channel_name(raw):
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<\name\>).+(?=\</\name\>)", raw)
    link = matches.group(0).strip()
    return link    

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        if request.args.get('hub.challenge', ''):
            return request.args.get('hub.challenge', '')

    elif request.method == 'POST':
        _log(LOGFILE, "Incoming webhook with following data: " + str(request.data))
        link = extract_link(request.data)

        db_retry_until_unlocked(LOGFILE, QUEUE_DIR, f'''
                                                     INSERT INTO queue (link)
                                                     VALUES (\'{link}\');
                                                     ''')
        _log(LOGFILE, f"Link \"{link}\" inserted!")
        return '200'

if __name__=='__main__':
    db_retry_until_unlocked(LOGFILE, QUEUE_DIR, '''
                                                CREATE TABLE IF NOT EXISTS queue
                                                (link text);
                                                ''')
    app.run()
