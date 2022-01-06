from bs4 import BeautifulSoup

from flask import Flask, request
flask_app = Flask(__name__)

from utils import Log
from ORM import SQL
from globals import *

LOGFILE = DIRECTION + CONFIG['server_linux_logfile']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
db = SQL(QUEUE_DIR)
db.create_table()
l = Log(LOGFILE)
#================================================================

def extract_by_name(content: bytes, name) -> str:
    return BeautifulSoup(content.decode('utf-8'), 'lxml').find(name).contents[0]

@flask_app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        return request.args.get('hub.challenge', None)

    elif request.method == 'POST':
        data = request.data
        l.log(f"Incoming webhook with following data: {data}")
        link = "https://youtube.com/watch?v=" + extract_by_name(data, "id")[9:]
        title = extract_by_name(data, "title")
        uploader = extract_by_name(data, "name")

        db.push_to_queue(link, title, uploader) 

        l.log(f'Link {link} from {uploader} inserted! ({title})')
        return '200'

if __name__ == '__main__':
    flask_app.run(debug=True, host="0.0.0.0", port=7777)
