import flask
from telegram_hh_bot import bot
from config import tg_bot_url
from config import hh_client_id, hh_secret, userbase_path
from hh_bot import get_user_access_token
from base.basemanage import UserManage


def hh_oauth_handler():
    if flask.request.args.get('error'):
        bot.send_message('Авторизация не удалась, попробуйте еще раз')
        return flask.redirect(tg_bot_url)
    user_chat_id = flask.request.args.get('state')
    auth_code = flask.request.args.get('code')
    access_token, refresh_token, acc_token_expire = get_user_access_token(hh_client_id, hh_secret, auth_code)
    userm = UserManage(userbase_path, user_chat_id)
    userm.set_user_tokens(access_token, refresh_token, int(acc_token_expire))
    bot.send_message('Авторизация прошла успешно')

    return flask.redirect(tg_bot_url)
