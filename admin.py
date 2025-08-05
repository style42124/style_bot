import telebot
from telebot import types

bot = telebot.TeleBot('8361205520:AAH2iVuuBv_KIKER5uP6X7A4Aj1QKkVwtvs')
admin_id = 7144631992


@bot.message_handler(commands=['test'])
def send_test(message):
    if message.from_user.id == admin_id:
        bot.send_message(message.chat.id, "Бот активен ✅")


@bot.message_handler(content_types=['text', 'photo', 'document', 'sticker', 'video', 'audio', 'voice'])
def handle_message(message):
    if message.from_user.id == admin_id:
        return

    user_info = f"👤 @{message.from_user.username}\n🆔 {message.from_user.id}\n📅 {message.date}\n---\n"

    markup = types.InlineKeyboardMarkup()
    reply_btn = types.InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_{message.from_user.id}")
    markup.add(reply_btn)

    if message.text:
        bot.send_message(admin_id, user_info + message.text, reply_markup=markup)
    elif message.photo:
        bot.send_photo(admin_id, message.photo[-1].file_id, caption=user_info, reply_markup=markup)
    elif message.document:
        bot.send_document(admin_id, message.document.file_id, caption=user_info, reply_markup=markup)
    elif message.sticker:
        bot.send_sticker(admin_id, message.sticker.file_id)
        bot.send_message(admin_id, user_info, reply_markup=markup)

    bot.send_message(message.chat.id, "✅ Сообщение доставлено")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply(call):
    user_id = int(call.data.split('_')[1])
    msg = bot.send_message(admin_id, f"Введите ответ для пользователя {user_id}:")
    bot.register_next_step_handler(msg, lambda m: process_reply(m, user_id))


def process_reply(message, user_id):
    try:
        if message.text:
            bot.send_message(user_id, f"📨 Вот и ваш ответ:\n\n{message.text}")
        elif message.photo:
            bot.send_photo(user_id, message.photo[-1].file_id)
        elif message.document:
            bot.send_document(user_id, message.document.file_id)

        bot.send_message(admin_id, "✅ Ответ отправлен")
    except:
        bot.send_message(admin_id, "⚠️ Ошибка отправки ответа")

if __name__ == '__main__':
    print("Бот запущен и работает")
    bot.infinity_polling()