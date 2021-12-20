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
    return re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", 
                    raw.decode('utf-8')
    ).group(0).strip()

def extract_channel_name(raw: bytes) -> str:
    return re.search(r"(?<=\<\name\>).+(?=\</\name\>)", 
                    raw.decode('utf-8')
    ).group(0).strip()
      

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        if request.args.get('hub.challenge', ''):
            return request.args.get('hub.challenge', '')

    elif request.method == 'POST':
        l.log(f"Incoming webhook with following data: {request.data}")
        link = extract_link(request.data)
        # TODO extract more info from the webhook data,
        # so that there will be no need to rely on youtube-dl
        # again during the posting stage
        db.push_to_queue(link)
        
        l.log(f'Link "{link}" from inserted!')
        return '200'

if __name__=='__main__':
    db.create_table()
    app.run()
