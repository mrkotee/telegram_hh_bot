
from hh_bot import invalidate_access_token
from base.basemanage import UserManage
from config import userbase_path


def delete_user_tokens(user_id):
    userm = UserManage(userbase_path, user_id)
    invalidate_access_token(userm.get_user_access_token())
    userm.delete_user_tokens()
