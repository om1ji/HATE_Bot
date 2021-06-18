from flask import Flask, request, render_template, url_for
import re, os, shutil
import telebot, json, requests
from regex import *

app = Flask(__name__)

DIRECTION = r'/home/bot/HATE/Files/'
TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
BOT = telebot.TeleBot(TOKEN)

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

        os.chdir(DIRECTION)
        os.system('youtube-dl -x https://www.youtube.com/watch?v={} --audio-format mp3 --audio-quality 0 --write-description -o "./%(id)s/%(title)s-%(id)s.%(ext)s" --write-thumbnail'.format(link))

        folder = DIRECTION + link + '/' #Путь до папки
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

        # caption = final(track_descr.read())

        BOT.send_audio(CHAT_ID, audio=file_itself.content, performer=artist(read_track_descr), title=title(read_track_descr))

        track_descr.close()
        single_file['document'].close()

        BOT.delete_message(-1001170446896, message_id)
        shutil.rmtree(DIRECTION + extract_link(request.data))
        return '200'        


if __name__=='__main__':
    app.run()
