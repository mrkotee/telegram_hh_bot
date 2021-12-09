import telebot

from config import telegram_token
from config import userbase_path, base_path
from config import redirect_uri, hh_client_id
from hh_bot import create_auth_url, get_user_resumes, get_resume_url
from base.basemanage import UserManage, ResumesManage


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


@bot.message_handler(commands=['my_resumes'])
def send_user_resumes(message):
    userm = UserManage(userbase_path, message.chat.id)
    resumes = get_user_resumes(userm.get_user_access_token())
    if resumes:
        msg = "Выберите резюме для подборки вакансий\n"
        markup = telebot.types.InlineKeyboardMarkup()
        for resume_id, resume_title in resumes.items():
            ResumesManage(userbase_path, resume_id, resume_title, userm.user.id)
            markup.add(telebot.types.InlineKeyboardButton(text=resume_title, callback_data=f"resume_id {resume_id}"))
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    else:
        msg = "Не могу найти ни одного резюме"
        bot.send_message(message.chat.id, msg)


@bot.callback_query_handler(func=lambda c: c.data.startswith('resume_id '))
def resume_settings(call):
    resume_id = call.data.split()[1]
    resumem = ResumesManage(userbase_path, resume_id)
    if not resumem.resume:
        bot.answer_callback_query(callback_query_id=call.id, text="Резюме не найдено в базе")
        return False
    msg = resumem.resume.name
    markup = telebot.types.InlineKeyboardMarkup()

    if resumem.resume.active:
        msg += "\nПоиск вакансий по резюме включен"
        search_btn_text = "Выключить поиск вакансий"
        search_btn_val = "off"
    else:
        search_btn_text = "Включить поиск вакансий"
        search_btn_val = "on"
    markup.add(telebot.types.InlineKeyboardButton(text=search_btn_text,
                                                  callback_data=f"search {resume_id} {search_btn_val}"))

    if resumem.resume.autoupdate:
        a_update_btn_text = "Включить автопубликацию"
        a_update_btn_val = 'on'
    else:
        a_update_btn_text = "Выключить автопубликацию"
        a_update_btn_val = 'off'
    markup.add(telebot.types.InlineKeyboardButton(text=a_update_btn_text,
                                                  callback_data=f"autoupdate {resume_id} {a_update_btn_val}"))

    btn = telebot.types.InlineKeyboardButton(text="Открыть резюме", url=get_resume_url(resume_id))
    markup.add(btn)

    bot.edit_message_text(text=msg, message_id=call.message.message_id,
                          chat_id=call.message.chat.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('search '))
def swith_resume_active(call):
    _, resume_id, swith_opt = call.data.split()
    resumem = ResumesManage(userbase_path, resume_id)
    msg = resumem.resume.name
    if swith_opt == 'on':
        resumem.swith_active(True)
        msg += "\nПоиск вакансий по резюме включен"
        search_btn_text = "Выключить поиск вакансий"
        search_btn_val = "off"
    else:
        resumem.swith_active(False)
        search_btn_text = "Включить поиск вакансий"
        search_btn_val = "on"

    markup = call.message.reply_markup
    for btn in markup.keyboard:
        if call.data == btn[0].callback_data:
            markup_btn = btn[0]
            markup_btn.text = search_btn_text
            markup_btn.callback_data = f"search {resume_id} {search_btn_val}"
            break

    bot.edit_message_text(text=msg, message_id=call.message.message_id,
                          chat_id=call.message.chat.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('autoupdate '))
def swith_resume_autoupdate(call):
    _, resume_id, update_opt = call.data.split()
    resumem = ResumesManage(userbase_path, resume_id)

    if update_opt == 'on':
        resumem.enable_autoupdate()
        a_update_btn_text = "Выключить автопубликацию"
        a_update_btn_val = 'off'
    else:
        resumem.disable_autoupdate()
        a_update_btn_text = "Включить автопубликацию"
        a_update_btn_val = 'on'

    markup = call.message.reply_markup
    for btn in markup.keyboard:
        if call.data == btn[0].callback_data:
            markup_btn = btn[0]
            markup_btn.text = a_update_btn_text
            markup_btn.callback_data = f"autoupdate {resume_id} {a_update_btn_val}"
            break

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

