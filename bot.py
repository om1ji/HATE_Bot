import telebot
from telebot import types
import sqlite3

TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id INTEGER
        yt_ch TEXT
        tg_ch INTEGER
    )""")
    connect.commit()

    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user_id = [message.chat.id]
        cursor.execute("INSERT INTO login_id VALUES(?);", user_id)
        connect.commit()
    else:
        print('Пользователь ' + message.chat.username + ' повторно зарегался')

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Подписаться')
    itembtn2 = types.KeyboardButton('Отписаться')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, 'Приветствую!', reply_markup=markup)
    markup = types.ReplyKeyboardRemove(selective=False)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.polling()