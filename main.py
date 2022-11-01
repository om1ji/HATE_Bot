from flask import Flask, request

import telegram
import yt_dlp

import os
import re
import threading

TOKEN = ""
CHANNEL_ID = 0 # Integer
DIR = r"" #Full path to the folder where temporary files will be located

FLASK_APP = Flask(__name__)
BOT = telegram.Bot(token=TOKEN)

os.chdir(DIR)

ydl_opts = {'format': "251",
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        'outtmpl': './%(title)s.%(ext)s', "writethumbnail": True}

def metadata(title: str) -> str:
    r = re.search(r"(.+)(?: - )(.+)(?:\[)", title) # Get Artist name and Track name
    return (r.group(1), r.group(2))
    
def send(url): # Sends to defined channel/chat
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.sanitize_info(ydl.extract_info(url, download=False))
        if data['duration'] < 1300: # Check if not Podcast, else skip
            ydl.download(url) # Download file
            artist, track_title = metadata(data['title'])
            title = data["title"]
            BOT.sendAudio(chat_id=CHANNEL_ID, 
                        audio = open(title+".mp3", 'rb'),
                        caption = f"""<a href="{data['original_url']}">Original upload</a>""",
                        performer = artist,
                        title = track_title, 
                        thumb=open(title+".webp", 'rb'), 
                        duration=data["duration"],
                        parse_mode="HTML")
            os.remove(title+".mp3")
            os.remove(title+".webp")

@FLASK_APP.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': 
        print(request)
        return request.args.get('hub.challenge', None) # PubSubHubbub auth

    elif request.method == 'POST':
        url = "https://www.youtube.com/watch?v=" + re.search(r"(?<=<yt:videoId>)(.*)(?=<\/yt:videoId>)", str(request.data)).group(1).strip()
        threading.Thread(target=send, args=[url]).start()
        return '200'

if __name__ == '__main__':
    FLASK_APP.run(host="0.0.0.0", port=7777)
