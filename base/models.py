from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime as dt
import os


Base = declarative_base()
UserBase = declarative_base()


class Users(UserBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    name = Column(String)
    add_date = Column(DateTime)
    active = Column(Boolean)
    hh_access_token = Column(String)
    hh_acc_token_exp = Column(DateTime)
    hh_refresh_token = Column(String)
    user_resumes = relationship("UserResumes", backref="user")

    def __init__(self, chat_id, name):
        self.chat_id = chat_id
        self.name = name
        self.add_date = dt.now()
        self.active = True


class UserResumes(UserBase):
    __tablename__ = 'userresumes'
    id = Column(Integer, primary_key=True)
    resume_id = Column(String)
    name = Column(String)
    keywords = Column(String)
    autoupdate = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, hh_resume_id, name: str, keywords: str = None, autoupdate=False):
        self.resume_id = hh_resume_id
        self.name = name
        if keywords:
            self.keywords = keywords
        self.autoupdate = autoupdate


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


def create_base_files(base_path):
    if not os.path.exists(base_path):
        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        UserBase.metadata.create_all(bind=engine)


if __name__ == "__main__":
    from config import base_path, userbase_path
    create_base_files(base_path)
    create_base_files(userbase_path)
