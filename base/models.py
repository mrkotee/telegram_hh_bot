from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime as dt
import os


Base = declarative_base()
UserBase = declarative_base()


class Users(UserBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    name = Column(String)
    add_date = Column(DateTime)
    active = Column(Boolean)
    hh_access_token = Column(String)
    hh_acc_token_exp = Column(DateTime)
    hh_refresh_token = Column(String)

    def __init__(self, chat_id, name):
        self.chat_id = chat_id
        self.name = name
        self.add_date = dt.now()
        self.active = True


class UserResumes(UserBase):
    __tablename__ = 'userresumes'
    id = Column(Integer, primary_key=True)
    resume_id = Column(String)
    keywords = Column(String)
    autorefresh = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, hh_resume_id, keywords: str = None, autorefresh=False):
        self.resume_id = hh_resume_id
        if keywords:
            self.keywords = keywords
        self.autorefresh = autorefresh


class Vacancies(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    name = Column(String)
    description = Column(Text)
    add_date = Column(DateTime)
    sended = Column(Boolean)
    resume_id = Column(Integer)

    def __init__(self, url, name, description, resume_id: int = None):
        """resume id from base"""
        self.url = url
        self.name = name
        self.description = description
        self.add_date = dt.now()
        self.sended = False
        if resume_id:
            self.resume_id = resume_id

    def text(self):
        return '*{}*\n{}\n{}'.format(self.name, self.description, self.url)


if __name__ == "__main__":
    from config import base_path, userbase_path
    if not os.path.exists(base_path):
        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        UserBase.metadata.create_all(bind=engine)

    if not os.path.exists(userbase_path):
        engine = create_engine('sqlite:///%s' % userbase_path, echo=False)
        UserBase.metadata.create_all(bind=engine)
