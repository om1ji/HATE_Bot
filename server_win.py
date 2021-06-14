from flask import Flask, request
import re, os
import telebot, json, requests
from regex import *

app = Flask(__name__)

direction = r'E:\Python\for_artemetra\Files'
TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
bot = telebot.TeleBot(TOKEN)

def extract_link(raw):
    raw = raw.decode('utf-8')
    matches = re.search(r"(?<=\<yt\:videoId\>).+(?=\<\/yt\:videoId\>)", raw)
    link = matches.group(0).strip()
    return link

def download(link, direction=direction):
    os.chdir(direction)
    os.system('youtube-dl -x https://www.youtube.com/watch?v={} --audio-format mp3 --audio-quality 0 --write-description -o ./%(title)s.%(ext)s'.format(link))

def init():
    return os.listdir(direction)

def send_HATE(description_path, audio_file_path):

    descr = open(description_path, 'r')
    descr = descr.read()

    single_file = {'document': open(audio_file_path, 'rb')}

    print('Начинаем отправку\n')
    the_file = requests.post("https://api.telegram.org/bot1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s/sendDocument?chat_id=-1001170446896", files=single_file)

    file_id = json.loads(the_file.text)['result']['audio']['file_id']
    message_id = json.loads(the_file.text)['result']['message_id']

    file_path = bot.get_file(file_id).file_path
    file_itself = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_path))

    caption = """Artists: #{artist}
Label: #{label}
Catalogue: #{catalogue}
Genre/Style: #{genre}, {style}""".format(artist = artist(descr), label = label(descr), catalogue = catalogue(descr), genre = genre(descr), style = style(descr))

    bot.send_audio(CHAT_ID, audio=file_itself.content, caption=caption, performer=artist(descr), title=title(descr))

    single_file['document'].close()

    bot.delete_message(-1001170446896, message_id)
    os.remove(audio_file_path)
    os.remove(description_path)


@app.route('/')
def index():
    return 'Bruh'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print(request)
        if request.args.get('hub.challenge', ''):
            return request.args.get('hub.challenge', '')

    elif request.method == 'POST':
        print('Входящий вебхук!\n')
        download(extract_link(request.data))
        send_HATE(init()[0], init()[1])
        return '200'

if __name__=='__main__':
    app.run(port=8080, host='0.0.0.0')