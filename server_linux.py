from flask import Flask, request, render_template, url_for
import re, os, shutil
import telebot, json, requests
from regex import *
import sqlite3


app = Flask(__name__)

DIRECTION = r'/home/bot/HATE/Files/'
TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
BOT = telebot.TeleBot(TOKEN)

_con = sqlite3.connect('/home/bot/HATE/Files/queue.db')
cur = _con.cursor()

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
        print('\nВходящий вебхук!\n')
        print(request.data)
        link = extract_link(request.data)
        cur.execute('''INSERT INTO queue
                    (link)
                    VALUES (\'{}\')
                    '''.format(link))
        _con.commit()


if __name__=='__main__':
    cur.execute('''CREATE TABLE IF NOT EXISTS queue
               (link text)''')
    app.run()
