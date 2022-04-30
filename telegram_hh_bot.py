import logging
import time
import telebot

try:
    from config import telegram_token
    from config import userbase_path, base_path
    from config import redirect_uri, hh_client_id
    from hh_bot import create_auth_url, get_user_resumes, get_resume_url, publish_resume
    from base.basemanage import UserManage, ResumesManage
except ImportError:
    from .config import telegram_token
    from .config import userbase_path, base_path
    from .config import redirect_uri, hh_client_id
    from .hh_bot import create_auth_url, get_user_resumes, get_resume_url, publish_resume
    from .base.basemanage import UserManage, ResumesManage

LOG_FILENAME = "hhbot.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
                    format=u'%(levelname)-8s [%(asctime)s]  %(message)s')
logTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

telebot.logger = logging

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
        msg = 'Здравствуй, {username}\nЧтобы начать пользоваться ботом, нужно авторизироваться через hh.ru.'.format(username=username)

        bot.send_message(chat_id, msg, reply_markup=markup)

    else:
        msg = "Уведомления уже включены"

        bot.send_message(chat_id, msg)


@bot.message_handler(commands=['my_resumes'])
def send_user_resumes(message):
    userm = UserManage(userbase_path, message.chat.id)
    if not userm.get_user_access_token():
        send_welcome(message)
        return None

    resumes = get_user_resumes(userm.get_user_access_token())
    if resumes:
        msg = "Выберите резюме для подборки вакансий\n"
        markup = telebot.types.InlineKeyboardMarkup()
        for resume_id, resume_title in resumes.items():
            ResumesManage(userbase_path, resume_id, resume_title, userm.user.id)
            markup.add(telebot.types.InlineKeyboardButton(text=resume_title, callback_data="resume_id {resume_id}".format(
                                                                                                                resume_id=resume_id)))
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
                                                  callback_data="search {resume_id} {search_btn_val}".format(resume_id=resume_id, 
                                                                            search_btn_val=search_btn_val)))

    if resumem.resume.autoupdate:
        a_update_btn_text = "Включить автопубликацию"
        a_update_btn_val = 'on'
    else:
        a_update_btn_text = "Выключить автопубликацию"
        a_update_btn_val = 'off'
    markup.add(telebot.types.InlineKeyboardButton(text=a_update_btn_text,
                                                  callback_data="autoupdate {resume_id} {a_update_btn_val}".format(
                                                    resume_id=resume_id, a_update_btn_val=a_update_btn_val)))

    markup.add(telebot.types.InlineKeyboardButton(text="Опубликовать резюме",
                                                  callback_data="publish {resume_id}".format(resume_id=resume_id)))

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

    try:
        markup = call.message.reply_markup
        for btn in markup.keyboard:
            if call.data == btn[0].callback_data:
                markup_btn = btn[0]
                markup_btn.text = search_btn_text
                markup_btn.callback_data = "search {resume_id} {search_btn_val}".format(resume_id=resume_id, 
                                                                                search_btn_val=search_btn_val)
                break

        bot.edit_message_text(text=msg, message_id=call.message.message_id,
                              chat_id=call.message.chat.id, reply_markup=markup)
    except AttributeError:
        new_markup = telebot.types.InlineKeyboardMarkup()
        markup = call.message.json['reply_markup']
        for btn in markup['inline_keyboard']:
            text = btn[0]['text']
            if 'callback_data' in btn[0]:
                if call.data == btn[0]['callback_data']:
                    markup_btn = btn[0]
                    text = search_btn_text
                    markup_btn['callback_data'] = "search {resume_id} {search_btn_val}".format(resume_id=resume_id,
                                                                                               search_btn_val=search_btn_val)
                new_markup.add(telebot.types.InlineKeyboardButton(text=text,
                                                  callback_data=btn[0]['callback_data']))
            elif 'url' in btn[0]:
                new_markup.add(telebot.types.InlineKeyboardButton(text=text,
                                                  url=btn[0]['url']))
        bot.edit_message_text(text=msg, message_id=call.message.message_id,
                              chat_id=call.message.chat.id, reply_markup=new_markup)



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


    try:
        markup = call.message.reply_markup
        for btn in markup.keyboard:
            if call.data == btn[0].callback_data:
                markup_btn = btn[0]
                markup_btn.text = a_update_btn_text
                markup_btn.callback_data = "autoupdate {resume_id} {a_update_btn_val}".format(resume_id=resume_id, 
                                                                                a_update_btn_val=a_update_btn_val)
                break
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    except AttributeError:
        new_markup = telebot.types.InlineKeyboardMarkup()
        markup = call.message.json['reply_markup']
        for btn in markup['inline_keyboard']:
            text = btn[0]['text']
            if 'callback_data' in btn[0]:
                if call.data == btn[0]['callback_data']:
                    markup_btn = btn[0]
                    text = a_update_btn_text
                    markup_btn['callback_data'] = "autoupdate {resume_id} {a_update_btn_val}".format(resume_id=resume_id,
                                                                                a_update_btn_val=a_update_btn_val)
                new_markup.add(telebot.types.InlineKeyboardButton(text=text,
                                                  callback_data=btn[0]['callback_data']))
            elif 'url' in btn[0]:
                new_markup.add(telebot.types.InlineKeyboardButton(text=text,
                                                  url=btn[0]['url']))

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=new_markup)
        



@bot.callback_query_handler(func=lambda c: c.data.startswith('publish '))
def swith_resume_autoupdate(call):
    userm = UserManage(userbase_path, call.message.chat.id)
    resume_id = call.data.split()[1]

    if publish_resume(userm.get_user_access_token(), resume_id):
        bot.answer_callback_query(callback_query_id=call.id, text="Резюме опубликовано")
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Ошибка")

