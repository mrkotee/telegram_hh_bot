
import time
from datetime import timedelta
from datetime import datetime as dt
import telebot
from telebot.apihelper import ApiException
from config import base_path, userbase_path
from base.basemanage import VacancyManage, UserManage, ResumesManage
from telegram_hh_bot import bot


def send_vacancies():
    vacancy_manage = VacancyManage(base_path)

    users_m = UserManage.get_all_users(userbase_path)

    for user_m in users_m:

        not_sended = vacancy_manage.get_not_sended_vacancies_by_user(user_m.user.id)
        if len(not_sended) > 50:
            not_sended = [vac for vac in not_sended if timedelta(days=1) > (dt.now() - vac.creation_date)]
        if len(not_sended) > 50:
            not_sended = [vac for vac in not_sended if timedelta(hours=10) > (dt.now() - vac.creation_date)]
        if len(not_sended) > 50:
            not_sended = not_sended[:50]

        for vacancy in not_sended:
            msg = '*{}*\n{}'.format(vacancy.name, vacancy.description)

            markup = telebot.types.InlineKeyboardMarkup()
            btn = telebot.types.InlineKeyboardButton(text="Открыть вакансию", url=vacancy.url)
            markup.add(btn)

            if len(msg) > 3000:
                msgs = []
                while len(msg) > 3000:
                    cut_point = msg.find('\n', 2500, 3500)
                    if cut_point == -1:
                        cut_point = 3000
                    msgs.append(msg[:cut_point])
                    msg = msg[cut_point:]

                for _msg in msgs:
                    bot.send_message(id, _msg, parse_mode='Markdown')
                    time.sleep(1)

            try:
                bot.send_message(user_m.user.chat_id, msg, parse_mode='Markdown', reply_markup=markup)
            except ApiException:
                try:
                    bot.send_message(user_m.user.chat_id, msg, reply_markup=markup)
                except ApiException:
                    bot.send_message(user_m.user.chat_id,
                                     'Something wrong with vacancy id {}'.format(vacancy.id), reply_markup=markup)
                    continue

            vacancy_manage.set_vacancy_sended(vacancy)
            time.sleep(1)


if __name__ == "__main__":
    send_vacancies()
