import telebot
from telebot import types
import random
import requests
from bs4 import BeautifulSoup
import wikipedia
import qrcode
from io import BytesIO
import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot('8431912273:AAHEfoM9isC9Nk3LGnXKB7d6Rp9_PxTLTDU')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            '🎲 Случайное число',
            '🦉 Википедия',
            '💰 Курс валют',
            '🎯 Игры',
            '🔮 Предсказание',
            '📊 Опрос'
        ]
        markup.add(*[types.KeyboardButton(btn) for btn in buttons])

        bot.send_message(
            message.chat.id,
            f"Привет, {message.from_user.first_name}! Я - функциональный бот!\n"
            "Выбери действие из меню или напиши /help",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📜 Доступные команды:
/start - Начать общение
/help - Помощь по командам  
/joke - Случайная шутка
/qr [текст] - QR-код
/time - Текущее время
/cat - Случайный котик
/dice - Игра в кости
/quiz - Викторина
"""
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda msg: msg.text == '🎲 Случайное число')
def random_number(message):
    try:
        num = random.randint(1, 100)
        bot.send_message(message.chat.id, f'🎲 Ваше число: {num}')
    except Exception as e:
        logger.error(f"Error in random_number: {e}")


@bot.message_handler(func=lambda msg: msg.text == '🦉 Википедия')
def ask_wikipedia(message):
    msg = bot.send_message(message.chat.id, '🔍 Что ищем в Википедии?')
    bot.register_next_step_handler(msg, process_wikipedia)


def process_wikipedia(message):
    try:
        wikipedia.set_lang("ru")
        summary = wikipedia.summary(message.text, sentences=2)
        bot.send_message(message.chat.id, summary)
    except wikipedia.exceptions.DisambiguationError as e:
        bot.send_message(message.chat.id, f"Уточните запрос: {e.options[:5]}")
    except Exception as e:
        logger.error(f"Wiki error: {e}")
        bot.send_message(message.chat.id, "😕 Не удалось найти информацию")


@bot.message_handler(func=lambda msg: msg.text == '💰 Курс валют')
def exchange_rates(message):
    try:
        response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp')
        soup = BeautifulSoup(response.content, 'xml')

        currencies = {
            'USD': 'R01235',
            'EUR': 'R01239'
        }

        result = "💱 Курсы валют:\n"
        for name, code in currencies.items():
            value = soup.find('Valute', ID=code).Value.text
            result += f"{name}: {value} руб.\n"

        bot.send_message(message.chat.id, result)
    except Exception as e:
        logger.error(f"Exchange error: {e}")
        bot.send_message(message.chat.id, "⚠️ Не удалось получить курсы")


@bot.message_handler(func=lambda msg: msg.text == '🎯 Игры')
def games_menu(message):
    try:
        markup = types.InlineKeyboardMarkup()
        games = [
            ('🎲 Кости', 'dice'),
            ('🎯 Дартс', 'dart'),
            ('🏀 Баскетбол', 'basketball')
        ]
        for text, callback in games:
            markup.add(types.InlineKeyboardButton(text, callback_data=callback))

        bot.send_message(message.chat.id, '🎮 Выберите игру:', reply_markup=markup)
    except Exception as e:
        logger.error(f"Games error: {e}")


@bot.callback_query_handler(func=lambda call: True)
def handle_games(call):
    try:
        emoji_map = {
            'dice': '🎲',
            'dart': '🎯',
            'basketball': '🏀'
        }
        if call.data in emoji_map:
            bot.send_dice(call.message.chat.id, emoji=emoji_map[call.data])
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Game callback error: {e}")


@bot.message_handler(commands=['qr'])
def generate_qr(message):
    try:
        text = message.text[4:].strip()
        if not text:
            return bot.send_message(message.chat.id, "Укажите текст: /qr ваш_текст")

        img = qrcode.make(text)
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)

        bot.send_photo(message.chat.id, bio, caption=f"QR-код для: {text}")
    except Exception as e:
        logger.error(f"QR error: {e}")
        bot.send_message(message.chat.id, "⚠️ Ошибка генерации QR-кода")

if __name__ == '__main__':
    logger.info("Бот main запущен!")
    bot.infinity_polling()