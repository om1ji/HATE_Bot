from flask import Flask, request, render_template, url_for
import re, os, shutil
import telebot, json, requests
from regex import *
import sqlite3
import time

DIRECTION = r'/home/bot/HATE/Files/'
queue_dir = r'/home/bot/HATE/Files/queue.db'
TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
BOT = telebot.TeleBot(TOKEN)




def extract_link(raw):
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", raw)
    link = matches.group(0).strip()
    return link

def download_from_queue(queue_dir):
    os.chdir(DIRECTION)
    _con = sqlite3.connect(queue_dir)
    cur = _con.cursor() 
    while True:
        cur.execute("SELECT * FROM queue")
        current_link = cur.fetchone()
        if current_link:
            # Run downloading
            os.system("""youtube-dl -x https://www.youtube.com/watch?v={} 
                        --audio-format mp3 --audio-quality 0 
                        --write-description -o "./%(id)s/%(title)s-%(id)s.%(ext)s" 
                        --write-thumbnail"""
                        .format(current_link))

            folder = DIRECTION + current_link + '/' #Путь до папки
            os.chdir(folder)
            basename = os.path.splitext(os.listdir()[0])[0]

            track_descr = folder + basename + '.description' #Путь до файла .description
            track_descr = open(track_descr)
            read_track_descr = track_descr.read()

            single_file = {'document': open(folder + basename + '.mp3', 'rb')}

            print('\nНачинаем отправку\n')
            the_file = requests.post("https://api.telegram.org/bot1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s/sendDocument?chat_id=-1001170446896", files=single_file)

            file_id = json.loads(the_file.text)['result']['document']['file_id']
            message_id = json.loads(the_file.text)['result']['message_id']

            file_path = BOT.get_file(file_id).file_path
            file_itself = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_path))

            caption = get_final_caption(track_descr.read())

            BOT.send_audio(CHAT_ID, audio=file_itself.content, caption=caption, performer=get_artist(read_track_descr), title=get_title(read_track_descr))

            track_descr.close()
            single_file['document'].close()

            BOT.delete_message(-1001170446896, message_id)
            shutil.rmtree(DIRECTION + extract_link(request.data))
            
            cur.execute("""DELETE FROM queue,
                        WHERE rowid=1;
                        """)

            _con.commit()

            return '200'  
        time.sleep(30)

if __name__ == '__main__':
    download_from_queue(queue_dir)