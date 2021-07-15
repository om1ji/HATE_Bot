import re
import sqlite3

from flask import Flask, request, render_template, url_for
import telebot

from regex import *
from _logging import _log

app = Flask(__name__)

DIRECTION = r'/home/bot/HATE/'
LOGFILE = DIRECTION + "server_linux-log.txt"

#================================================================

def extract_link(raw):
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", raw)
    link = matches.group(0).strip()
    return link
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/me')
def me():
    return render_template('Визитка.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        if request.args.get('hub.challenge', ''):
            return request.args.get('hub.challenge', '')

    elif request.method == 'POST':
        _log(LOGFILE, "Incoming webhook with following data: " + str(request.data))
        link = extract_link(request.data)

        _con = sqlite3.connect(DIRECTION + 'queue.db')
        cursor = _con.cursor()

        cursor.execute('''INSERT INTO queue
                    (link)
                    VALUES (\'{}\')
                    '''.format(link))
        _con.commit()
        _log(LOGFILE, f"Link \"{link}\" inserted!")
        return '200'

if __name__=='__main__':
    _con = sqlite3.connect(DIRECTION + 'queue.db')
    cursor = _con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS queue
               (link text)''')
    _con.commit()
    app.run()
