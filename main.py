from states import bot
from api import link
import json
import requests
from config import HISTORY_LIST
import pickle
import os
import atexit



# Запуск бота по команде /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот для поиска новостных статей!\n'
                                     'Чтобы посмотреть доступные команды напиши /help')


# Ответ бота на команду /help
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Команды для работы с ботом:\n'
                                      '/search - слово, по которому будет проводиться поиск\n'
                                      '/newest - самая свежая статья\n'
                                      '/oldest - самая старая статья\n'
                                      '/history - последние 10 запросов\n'
                                      '/help - доступные команды')


# Ответ бота на команду /search
@bot.message_handler(commands=['search'])
def search_message(message):
    msg = bot.send_message(message.from_user.id, 'Введите слово, а я найду статьи с его упоминанием!')
    bot.register_next_step_handler(msg, link_creator)



# Ответ бота на команду /newest
@bot.message_handler(commands=['newest'])
def newest_message(message):
    if os.path.isfile('Requests.pkl'):
        with open('Requests.pkl', 'rb') as requests_file:
            data = pickle.load(requests_file)

        articles = data['articles']
        date = ''
        for i_news in articles:
            if date == '':
                date = i_news['publishedAt']
            elif date <= i_news['publishedAt']:
                date = i_news['publishedAt']
                article = i_news

        bot.send_message(message.chat.id, article['url'])
    else:
        bot.send_message(message.chat.id, 'Еще не было запроса для поиска по слову\n'
                                          'для этого введите /search')



# Ответ бота на команду /oldest
@bot.message_handler(commands=['oldest'])
def oldest_message(message):
    if os.path.isfile('Requests.pkl'):
        with open('Requests.pkl', 'rb') as requests_file:
            data = pickle.load(requests_file)

        articles = data['articles']
        date = ''
        for i_news in articles:
            if date == '':
                date = i_news['publishedAt']
            elif date >= i_news['publishedAt']:
                date = i_news['publishedAt']
                article = i_news

        bot.send_message(message.chat.id, article['url'])
    else:
        bot.send_message(message.chat.id, 'Еще не было запроса для поиска по слову\n'
                                          'для этого введите /search')


# Ответ бота на команду /history
@bot.message_handler(commands=['history'])
def history_message(message):
    HISTORY_LIST.reverse()
    if len(HISTORY_LIST) == 0:
        bot.send_message(message.chat.id, 'Еще не было запросов(')
    else:
        while len(HISTORY_LIST) > 10:
            HISTORY_LIST.pop(10)

        bot.send_message(message.chat.id, 'Последние 10 запросов:')
        count = 0
        for i_request in HISTORY_LIST:
            count += 1
            bot.send_message(message.chat.id, f'{count}) {i_request}')


# Создание ссылки по запросу пользователя
def link_creator(message):
    HISTORY_LIST.append(message.text)
    new_link = link + str(message.text)
    req = requests.get(new_link)
    data = json.loads(req.text)
    if data['totalResults'] == 0:
        bot.send_message(message.chat.id, 'Статей по данному запросу не найдено :(')
    else:
        with open('Requests.pkl', 'wb') as requests_file:
            pickle.dump(data, requests_file)

        bot.send_message(message.from_user.id, 'Найти самую новую статью или самую старую?\n'
                                          'Чтобы найти самую новую, введите /newest\n'
                                          'Чтобы найти самую старую, введите /oldest')


bot.infinity_polling()

# Функция для удаления файла Requests.pkl после завершения работы программы
def exit_handler():
    if os.path.isfile('C:\\Users\\Данилкин\\PycharmProjects\\python_basic_diploma\\Requests.pkl'):
        os.remove('C:\\Users\\Данилкин\\PycharmProjects\\python_basic_diploma\\Requests.pkl')
    else:
        print('Файла не существует')

atexit.register(exit_handler)