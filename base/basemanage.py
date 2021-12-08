
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class BaseManage:

    def __init__(self):
        self.session = None

    def create_session(self, base_path):
        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        self.session = sessionmaker(bind=engine)()

        return self.session


class UserManage(BaseManage):

    def __init__(self, user: int = None):
        super.__init__()
        if user:
            try:
                self.get_user_by_id(user)
            except:  # sessionerror
                self.get_user_by_chat_id(user)

        self.user = None

    def get_user_by_id(self, user_id):
        pass

    def get_user_by_chat_id(self, chat_id):
        pass

    def get_user_access_token(self):
        return self.user.hh_access_token

    def get_user_refresh_token(self):
        return self.user.hh_refresh_token

    def set_user_tokens(self, access_token, refresh_token, access_token_expire_in: int = None):
        pass


class ResumesManage(BaseManage):

    def __init__(self, user):
        super.__init__()

        if isinstance(user, UserManage):
            self.user = user.user
        elif isinstance(user, int):
            self.UserManage(user)

    def get_user_resumes(self):
        pass


