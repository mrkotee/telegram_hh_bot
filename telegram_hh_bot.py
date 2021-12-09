import telebot

from config import telegram_token
from config import userbase_path, base_path
from config import redirect_uri, hh_client_id
from hh_bot import create_auth_url
from base.basemanage import UserManage


bot = telebot.TeleBot(telegram_token, threaded=False)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    username = message.chat.username

    usermanage = UserManage(userbase_path, chat_id, username)

    if not usermanage.get_user_access_token():
        uri = create_auth_url(hh_client_id, chat_id, redirect_uri)
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Авторизироваться", url=uri)
        markup.add(btn)
        msg = f'Здравствуй, {username}\nЧтобы начать пользоваться ботом, нужно авторизироваться через hh.ru.'

        bot.send_message(chat_id, msg, reply_markup=markup)

    else:
        msg = "Уведомления уже включены"

        bot.send_message(chat_id, msg)


@bot.message_handler(commands=['my_resume'])
def send_user_resumes(message):
    pass


@bot.message_handler(commands=['autorefresh'])
def set_autorefresh_user_resume(message):
    pass



########################
@bot.message_handler(commands=["test"])
def test(message):
    mark = telebot.types.InlineKeyboardMarkup()
    mark.add(telebot.types.InlineKeyboardButton(text='push me', callback_data='touch me'))

    bot.send_message(message.chat.id, 'such me', reply_markup=mark)


@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    bot.answer_callback_query(callback_query_id=call.id, text=call.message.text)  # popup msg

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # remove markup

@bot.message_handler(commands=['clear'])
def clear_markup_msg(message):
    bot.send_message(message.chat.id, 'clear markup', reply_markup=telebot.types.ReplyKeyboardRemove())
