# Строка 20 API-key bot
# Строка 98 API-key news

#Версия сырая, плохо работает интерфейс. Бд создается, данные сохраняются.

import sqlite3 as lite
from typing import List, Any
import telebot
from newsapi import NewsApiClient
i = 0
con = lite.connect('news_bd.db', check_same_thread=False)
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,'' f_name varchar(50), l_name varchar(50));')
cur.execute('CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,''cat_name varchar(100), user_id INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS keywords (keyword_id integer primary key AUTOINCREMENT,''word_name varchar(100), user_id INTEGER)')
data = cur.fetchone()
print(data)
bot = telebot.TeleBot("******", parse_mode=None)
kw = telebot.types.ReplyKeyboardMarkup(True)
kw.row('/show_news')
kw.row('Добавить категорию', 'Добавить ключевое слово')
kw.row('Просмотр категорий', 'Просмотр ключевых слов')
kw.row('Удалить категорию', 'Удалить ключевое слово')
def add_category(inp):
	cat_data = cur.execute(f"SELECT * FROM categories WHERE cat_name = '{inp.text}'").fetchone()
	if cat_data is None:
		cur.execute(f"INSERT INTO categories (cat_name, user_id) VALUES " f" ('{inp.text}'," f" {inp.from_user.id})")
		con.commit()
	else:
		bot.reply_to(inp, "(^.^)")
def add_keyword(inp):
	key_data = cur.execute(f"SELECT * FROM keywords WHERE word_name = '{inp.text}'").fetchone()
	if key_data is None:
		cur.execute(f"INSERT INTO keywords (word_name, user_id) VALUES " f" ('{inp.text}'," f" {inp.from_user.id})")
		con.commit()
	else:
		bot.reply_to(inp, "Уже есть")
def show_categories(inp):
	cats = cur.execute(f"SELECT cat_name FROM categories WHERE user_id = {inp.from_user.id}").fetchall()
	if cats is None:
		bot.reply_to(inp, "(^.^)")
	else:
		bot.reply_to(inp, f"Список категорий {cats}")
def show_keywords(inp):
	keys = cur.execute(f"SELECT word_name FROM keywords WHERE user_id = {inp.from_user.id}").fetchall()
	if keys is None:
		bot.reply_to(inp, "(^.^)")
	else:
		bot.reply_to(inp, f"Список ключевых слов: : {keys}")
def remove_category(inp):
	cur.execute(f"DELETE FROM categories WHERE cat_name = '{inp.text}'")
	con.commit()
def remove_keyword(inp):
	cur.execute(f"DELETE FROM keywords WHERE word_name = '{inp.text}'")
	con.commit()
@bot.message_handler(commands=['start'])
def send_welcome(inp):
	user_data = cur.execute(f"SELECT * FROM users WHERE user_id = {inp.from_user.id}").fetchone()
	if user_data is None:
		cur.execute(f"INSERT INTO users (user_id, f_name, l_name) VALUES "
					f" ({inp.from_user.id},"
					f" '{inp.from_user.first_name}',"
					f" '{inp.from_user.last_name}')")
		con.commit()
	bot.reply_to(inp, f"Добрый день {inp.from_user.first_name}\n Какие новости желаете посмотреть?",
				 reply_markup=kw)
@bot.message_handler(commands=['help'])
def send_welcome(inp):
	print(inp)
	bot.reply_to(inp, f"msg = {inp.text} Оо")
@bot.message_handler(commands=['show_news'])
def get_news(inp):
	bot.reply_to(inp, "Новости: \n")
	newsapi = NewsApiClient(api_key="******")
	cats: List[Any] = cur.execute(f"SELECT cat_name FROM categories WHERE user_id = {inp.from_user.id}").fetchall()
	keys: List[Any] = cur.execute(f"SELECT word_name FROM keywords WHERE user_id = {inp.from_user.id}").fetchall()
#Не работает...
	top_headlines = newsapi.get_top_headlines(q='Tesla', category='business')
	bot.reply_to(inp, f"{top_headlines['totalResults']} \n {top_headlines['articles'][0]['title']}")
@bot.message_handler(content_types=["text"])
def bot_news(inp):
	global i
	if i == 1:
		add_category(inp)
		i = 0
	elif i == 2:
		add_keyword(inp)
		i = 0
	elif i == 3:
		show_categories(inp)
		i = 0
	elif i == 4:
		show_keywords(inp)
		i = 0
	elif i == 5:
		remove_category(inp)
		i = 0
	else:
		remove_keyword(inp)
		i = 0
	bot.send_message(inp.chat.id, 'Готово', reply_markup=telebot.types.ReplyKeyboardRemove())
	if inp.text == "Добавить категорию":
		i = 1
		kw1 = telebot.types.ReplyKeyboardMarkup(True)
		kw1.row('busines', 'entertaiment')
		kw1.row('genegal', 'health', 'technology')
		kw1.row('science', 'sports')
		bot.send_message(inp.chat.id, "Возможные категории", reply_markup=kw1)
	elif inp.text == 'Добавить ключевое слово':
		i = 2
		bot.send_message(inp.chat.id, "Введите ключевое слово")
	elif inp.text == 'Просмотр категорий':
		i = 3
	elif inp.text == 'Просмотр ключевых слов':
		i = 4
	elif inp.text == 'Удалить категорию':
		i = 5
		bot.send_message(inp.chat.id, "Какую категорию удалить?")
		kw1 = telebot.types.ReplyKeyboardMarkup(True)
		kw1.row('busines', 'entertaiment')
		kw1.row('genegal', 'health', 'technology')
		kw1.row('science', 'sports')
		bot.send_message(inp.chat.id, "Возможные категории", reply_markup=kw1)
	elif inp.text == 'Удалить ключевое слово':
		i = 6
		bot.send_message(inp.chat.id, "Какое ключевое слово удалить?")
bot.polling()