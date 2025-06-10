# Телеграмм бот, играющий в 5 букв
import telebot
from telebot import types
import re
import datetime
import random
import bisect

with open('token.txt', 'r') as file:
    token = file.read()

bot = telebot.TeleBot(token)  # подключение токена бота
score = {'user': 0, 'bot': 0}

with open('my_words.txt', 'r', encoding='utf-8') as file:
    secret_word = random.choice([line.rstrip() for line in file.readlines()])  # слово, которое нужно угадать
positions = {1: [], 2: [], 3: [], 4: [], 5: []}  # содержит буквы, которые есть в слове, но не на своем месте
match = "_____"  # отгаданное слово
wrong_letters = []  # буквы, которых нет в слове
attempts = 7


# метод получения текстового сообщения
@bot.message_handler(commands=['start'])
def send_welcome(message):
    greeting = ''
    now = datetime.datetime.now()  # Текущее время
    if now.hour < 6:  # Время суток
        greeting = 'Доброй ночи'
    elif now.hour < 12:
        greeting = 'Доброе утро'
    elif now.hour < 18:
        greeting = 'Добрый день'
    else:
        greeting = 'Добрый вечер'

    bot.reply_to(message, greeting + '\nКак тебя зовут?')


@bot.message_handler(content_types=['text'])
def name(message):
    global username
    username = [', ' + message.text, '']
    keyboard = types.InlineKeyboardMarkup()  # Клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='rules_yes')  # Кнопка «Да»
    keyboard.add(key_yes)  # Добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='rules_no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text=f'Хочешь узнать правила {random.choice(username)}?', reply_markup=keyboard)
    bot.register_next_step_handler(message, attempt)


@bot.message_handler(content_types=['text'])
def attempt(message):
    global positions, match, wrong_letters, attempts
    word = re.findall("[а-яА-Я|ё|Ё]+", message.text)
    word = ''.join(word).lower().replace('ё', 'е')
    if len(word) != 5:
        with open('phrases/error.txt', 'r', encoding='utf-8') as file:
            bot.send_message(message.from_user.id, random.choice([line.rstrip() for line in file.readlines()]) +
                             random.choice(username))
    else:
        with open('phrases/step.txt', 'r', encoding='utf-8') as file:
            bot.send_message(message.from_user.id, random.choice([line.rstrip() for line in file.readlines()]) +
                             random.choice(username))
        for pos in range(5):
            if word[pos] == secret_word[pos]:
                if match[pos] == '_':
                    match = match[:pos] + word[pos] + match[pos + 1:]
            elif word[pos] in secret_word and word[pos] not in positions[pos + 1]:
                bisect.insort(positions[pos + 1], word[pos])
        mask = [secret_word[j] for j in range(5) if match[j] == '_']
        for symb in set(word):
            if symb not in secret_word and symb not in wrong_letters:
                bisect.insort(wrong_letters, symb)
            if symb in secret_word and symb not in mask:
                for i in range(1, 6):
                    if symb in positions[i]:
                        positions[i].remove(symb)
        if '_' not in match:
            with open('phrases/user_win.txt', 'r', encoding='utf-8') as file:
                bot.send_message(message.from_user.id, random.choice([line.rstrip() for line in file.readlines()]) +
                                 random.choice(username))
            score['user'] += 1
            final(message)
            return
        attempts -= 1
        if attempts == 0:
            with open('phrases/user_lost.txt', 'r', encoding='utf-8') as file:
                bot.send_message(message.from_user.id, random.choice([line.rstrip() for line in file.readlines()]) +
                                 random.choice(username))
                bot.send_message(message.from_user.id, 'Загаданное слово: ' + secret_word)
            score['bot'] += 1
            final(message)
            return
        bot.send_message(message.from_user.id, f'Слово: {str_match(match)}\n'
                                               f'Буквы, которые есть в слове, но не на своих позициях: {str_pos(positions)}\n'
                                               f'Буквы, которых нет в слове: {str_wl(wrong_letters)}\n'
                                               f'Осталось попыток: {attempts}')
        with open('phrases/ask.txt', 'r', encoding='utf-8') as file:
            bot.send_message(message.from_user.id, random.choice([line.rstrip() for line in file.readlines()])
                             + random.choice(username))
    bot.register_next_step_handler(message, attempt)


def str_match(match):
    return ' '.join(match)


def str_pos(pos):
    s = ''
    for key, value in pos.items():
        if len(value) != 0:
            t = ', '.join(value)
            if s == '':
                s = '\n\t' + str(key) + ': ' + t
            else:
                s = s + '\n\t' + str(key) + ': ' + t
    if s == '':
        s = 'таких нет'
    return s


def str_wl(wl):
    s = ', '.join(wl)
    if s == '':
        s = 'таких нет'
    return s


def final(message):
    text = 'Счёт\n' + username[0][2:] + ': ' + str(score['user']) + '\n' + 'бот: ' + str(score['bot'])
    bot.send_message(message.from_user.id, text=text)
    keyboard = types.InlineKeyboardMarkup()  # клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='cont_yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='cont_no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text=f'Хочешь продолжить{random.choice(username)}?',
                     reply_markup=keyboard)
    global positions, match, wrong_letters, attempts, secret_word
    with open('my_words.txt', 'r', encoding='utf-8') as file:
        secret_word = random.choice([line.rstrip() for line in file.readlines()])
    positions = {1: [], 2: [], 3: [], 4: [], 5: []}
    match = "_____"
    wrong_letters = []
    attempts = 7
    bot.register_next_step_handler(message, attempt)


def end(message):
    bye = ''
    # Получаем текущее время
    now = datetime.datetime.now()
    # Определяем время суток
    if now.hour < 6:
        greeting = 'Спокойной ночи'
    elif now.hour < 16:
        greeting = 'Хорошего дня'
    elif now.hour < 18:
        greeting = 'Хорошего вечера'
    else:
        greeting = 'Спокойной ночи'
    bot.reply_to(message, greeting)
    bot.polling().stop_bot()
    bot.delete_webhook()


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'rules_yes':
        with open('phrases/rules.txt', 'r', encoding='utf-8') as file:
            bot.send_message(call.message.chat.id, file.read())
        bot.send_message(call.message.chat.id, text=f'Введи 5 букв')
    elif call.data == 'rules_no':
        with open('phrases/beginnings.txt', 'r', encoding='utf-8') as file:
            bot.send_message(call.message.chat.id, random.choice([line.rstrip() for line in file.readlines()]) +
                             random.choice(username))
        bot.send_message(call.message.chat.id, text=f'Введи 5 букв')
    elif call.data == 'cont_no':
        end(call.message)
    elif call.data == 'cont_yes':
        bot.send_message(call.message.from_user.id, text='Давай сыграем еще раз\nВведи 5 букв')


bot.polling()
