from flask import Flask, request
import asyncio
import telegram
import yt_dlp

import os
import re

TOKEN = ""
CHANNEL_ID = 
DIR = r""

FLASK_APP = Flask(__name__)
BOT = telegram.Bot(token=TOKEN)

os.chdir(DIR)

ydl_opts = {
        'format': "251",
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': './%(title)s.%(ext)s',
        "writethumbnail": True
    }

#================================================================

async def send(url):

    data = ''

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)
        data = ydl.sanitize_info(ydl.extract_info(url, download=False))

    duration = data["duration"]

    BOT.sendAudio(chat_id=CHANNEL_ID, 
                        audio=open(DIR+data["title"]+".mp3", 'rb'), 
                        thumb=open(DIR+data["title"]+".webp", 'rb'), 
                        duration=duration)
    
    for f in os.listdir(DIR):
        os.remove(DIR+f)

    data = ""


@FLASK_APP.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': # PubSubHubbub auth
        print(request)
        return request.args.get('hub.challenge', None)

    elif request.method == 'POST':
        url = "https://www.youtube.com/watch?v=" + re.search(r"(?<=<yt:videoId>)(.*)(?=<\/yt:videoId>)", str(request.data)).group(1).strip()
        asyncio.run(send(url))
        return '200'

if __name__ == '__main__':
    FLASK_APP.run(host="0.0.0.0", port=7777)
    
