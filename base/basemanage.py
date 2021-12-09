import datetime
from datetime import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, ProgrammingError

from config import userbase_path, base_path
try:
    from models import Users, UserResumes, Vacancies
except ModuleNotFoundError:
    from base.models import Users, UserResumes, Vacancies


def check_session(func):
    def wrap(self, *args, **kwargs):
        if not self.session:
            self.create_session()
        return func(self, *args, **kwargs)
    return wrap


class BaseManage:

    def __init__(self, base_path, session=None):
        self.session = session
        self.base_path = base_path

    def create_session(self):
        engine = create_engine(f'sqlite:///{self.base_path}', echo=False)
        self.session = sessionmaker(bind=engine)()

        return self.session

    def close_session(self):
        self.session.close()

    def __del__(self):
        try:
            self.close_session()
        except ProgrammingError or AttributeError:
            pass


class UserManage(BaseManage):

    @classmethod
    def get_all_users(cls, base_path):
        engine = create_engine(f'sqlite:///{base_path}', echo=False)
        session = sessionmaker(bind=engine)()
        users = [UserManage(base_path, user.id, session=session) for user in session.query(Users).all()]
        return users

    def __init__(self, base_path, user_id: int = None, name: str = None, session=None):
        super().__init__(base_path, session)
        if user_id:
            if not self.get_user_by_id(user_id):
                self.get_user_by_chat_id(user_id)
            if not self.user and name:
                self.create_user(user_id, name)
        else:
            self.user = None

    @check_session
    def create_user(self, chat_id: int, name: str):
        self.session.add(Users(chat_id, name))
        self.session.commit()
        self.user = self.session.query(Users).filter(Users.chat_id == chat_id).first()

    @check_session
    def get_user_by_id(self, user_id):
        self.user = self.session.query(Users).get(user_id)
        return self.user

    @check_session
    def get_user_by_chat_id(self, chat_id):
        self.user = self.session.query(Users).filter(Users.chat_id == chat_id).first()
        return self.user

    def get_user_access_token(self):
        return self.user.hh_access_token

    def get_user_refresh_token(self):
        return self.user.hh_refresh_token

    def set_user_tokens(self, access_token: str, refresh_token: str, access_token_expire_in: int = None):
        self.user.hh_access_token = access_token
        self.user.hh_refresh_token = refresh_token
        if access_token_expire_in:
            self.user.hh_acc_token_exp = dt.fromtimestamp(access_token_expire_in)
        self.session.commit()

    def get_all_user_resumes_id(self):
        return [res.id for res in self.user.user_resumes]


class ResumesManage(BaseManage):

    @classmethod
    def get_all_resumes(cls, base_path):
        engine = create_engine(f'sqlite:///{base_path}', echo=False)
        session = sessionmaker(bind=engine)()
        users = [ResumesManage(base_path, resume.id, session=session) for resume in session.query(UserResumes).all()]
        return users

    def __init__(self, base_path, resume_id: int = None,
                 name: str = None, user_id: int = None, keywords: str = None, session=None):
        super().__init__(base_path, session)
        if resume_id:
            if isinstance(resume_id, int):
                self.get_user_resume_by_id(resume_id)
            elif isinstance(resume_id, str):
                if not self.get_resume_by_hh_id(resume_id):
                    if name and user_id:
                        if keywords:
                            self.add_resume(resume_id, name, user_id, keywords)
                        else:
                            self.add_resume(resume_id, name, user_id)
        else:
            self.resume = None

    @check_session
    def get_user_resume_by_id(self, resume_id: int):
        self.resume = self.session.query(UserResumes).get(resume_id)
        return self.resume

    @check_session
    def get_resume_by_hh_id(self, hh_resume_id: str):
        self.resume = self.session.query(UserResumes).filter(UserResumes.resume_id == hh_resume_id).first()
        return self.resume

    def enable_autoupdate(self):
        self.resume.autoupdate = True
        self.session.commit()

    def disable_autoupdate(self):
        self.resume.autoupdate = False
        self.session.commit()

    def swith_active(self, active=False):
        self.resume.active = active
        self.session.commit()

    @property
    def active(self):
        return self.resume.active

    def get_user_id(self):
        return self.resume.user.id

    def get_keywords(self):
        return self.resume.keywords

    def set_keywords(self, keywords: str):
        """
        set keywords to filter vacancies by resume
        :param keywords: is list of words separated by whitespace"""

        self.resume.keywords = keywords
        self.session.commit()

    @check_session
    def add_resume(self, hh_resume_id, resume_name, user_id, keywords: str = None):
        self.session.add(UserResumes(hh_resume_id, resume_name, user_id))
        self.session.commit()
        self.resume = self.get_resume_by_hh_id(hh_resume_id)
        if keywords:
            self.set_keywords(self.resume.id, keywords)
        return self.resume

    def delete_resume(self):
        self.session.delete(self.resume)
        self.session.commit()
        del self


class VacancyManage(BaseManage):

    def __init__(self, base_path, session=None):
        self.base_path = base_path
        self.session = session
        if not self.session:
            self.create_session()

    def get_not_sended_vacancies_by_resume(self, resume_id):

        return self.session.query(Vacancies).filter(
            Vacancies.resume_id == resume_id).filter(Vacancies.sended == False).all()

    def get_all_vacancies_by_resume(self, resume_id):

        return self.session.query(Vacancies).filter(
            Vacancies.resume_id == resume_id).all()[::-1]

    def get_not_sended_vacancies_by_user(self, user_id):

        return self.session.query(Vacancies).filter(
            Vacancies.user_id == user_id).filter(Vacancies.sended == False).all()

    def get_all_vacancies_by_user(self, user_id):
        return self.session.query(Vacancies).filter(Vacancies.user_id == user_id).all()[::-1]

    def get_vacancy_by_url(self, vacancy_url):
        return self.session.query(Vacancies).filter(Vacancies.url == vacancy_url).first()

    def get_vacancy_in_text(self, vacancy):
        if isinstance(vacancy, Vacancies):
            return vacancy.text()
        elif isinstance(vacancy, int):
            return self.session.query(Vacancies).get(vacancy)

    def set_vacancy_sended(self, vacancy):
        if isinstance(vacancy, Vacancies):
            vacancy.sended = True
        elif isinstance(vacancy, int):
            self.session.query(Vacancies).get(vacancy).sended = True
        self.session.commit()

    @check_session
    def add_vacancy(self, vacancy_url: str, vacancy_name: str, vacancy_description: str, creation_date: datetime.datetime,
                    resume_id: int, user_id: int):
        self.session.add(Vacancies(vacancy_url, vacancy_name, vacancy_description, creation_date, resume_id, user_id))
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return False
        vacancy = self.session.query(Vacancies).filter(Vacancies.url == vacancy_url).first()
        return vacancy

