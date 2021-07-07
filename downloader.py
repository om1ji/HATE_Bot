import os
import shutil
import json
import sqlite3
import time
import requests

import telebot

from regex import *
from _logging import _log

DIRECTION = r'/home/bot/HATE/'
RESULT_DIR = DIRECTION + 'tmp/'
QUEUE_DIR = DIRECTION + 'queue.db'
LOGFILE = DIRECTION + "downloader-log.txt"
TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
TMP_CHAT_ID = -1001170446896
BOT = telebot.TeleBot(TOKEN)


def download_from_queue(QUEUE_DIR):
    print(QUEUE_DIR)
    _con = sqlite3.connect(QUEUE_DIR)
    cur = _con.cursor() 
    while True:
        os.chdir(DIRECTION)
        cur.execute("SELECT * FROM queue")
        current_link = cur.fetchone()[0]
        if current_link:
            _log(LOGFILE, "Fetched link: " + str(current_link) + ", running downloading....")
            # Run downloading
            os.system(f"""youtube-dl -x {current_link} \
                        --audio-format mp3 --audio-quality 0 --no-part \
                        --write-description -o "./tmp/%(id)s/%(title)s-%(id)s.%(ext)s" \
                        --write-thumbnail""")
            _log(LOGFILE, "Downloading finished!", 1)
            folder = RESULT_DIR + current_link[-11:] + '/' #Путь до папки
            os.chdir(folder)
            basename = os.path.splitext(os.listdir()[0])[0]

            track_descr_path = folder + basename + '.description' #Путь до файла .description
            track_descr = open(track_descr_path) #Путь до файла .description
            read_track_descr = track_descr.read()
            _log(LOGFILE, f"Folder: {folder}, path to .description file: {track_descr_path}", 1)
            single_file = {'document': open(folder + basename + '.mp3', 'rb')}
            thumbnail = {'document': open(folder + basename + '.webp', 'rb')}

            _log(LOGFILE, "Sending to temp channel...", 1)
            the_file = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=single_file)
            the_thumb = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=thumbnail)
            
            try:
                file_id = json.loads(the_file.text)['result']['audio']['file_id']
                duration = json.loads(the_file.text)['result']['audio']['duration']
            except KeyError:
                file_id = json.loads(the_file.text)['result']['document']['file_id']
                duration = 0

            file_id = json.loads(the_file.text)['result']['document']['file_id']
            message_id = json.loads(the_file.text)['result']['message_id']
            _log(LOGFILE, "thumb result: " + str(json.loads(the_thumb.text)['result']), 1)
            thumb_id = json.loads(the_thumb.text)['result']['sticker']['thumb']['file_id']

            file_path = BOT.get_file(file_id).file_path
            _log(LOGFILE, f"File path: {file_path}; File id: {file_id}; Message id: {message_id}", 2)
            file_itself = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}')

            caption = get_final_caption(basename + '.description', read_track_descr)
            BOT.send_audio(CHAT_ID, audio=file_itself.content, 
                                    caption=caption, 
                                    performer=get_artist(basename + '.description'), 
                                    title=get_title(basename + '.description'),
                                    thumb=thumb_id,
                                    duration=duration)
            _log(LOGFILE, "Audio sent to the main channel!")

            track_descr.close()
            single_file['document'].close()

            BOT.delete_message(TMP_CHAT_ID, message_id)
            _log(LOGFILE, "Message deleted from temp channel", 1)
            shutil.rmtree(folder)
            _log(LOGFILE, f"Directory {folder} removed", 1)
            cur.execute("""DELETE FROM queue
                        WHERE rowid=1;
                        """)

            _con.commit()
            _log(LOGFILE, "Row deleted from the db", 1)
            _log(LOGFILE, "=CYCLE ENDED=" , 1)
        else:
            time.sleep(15)

if __name__ == '__main__':
    download_from_queue(QUEUE_DIR)
