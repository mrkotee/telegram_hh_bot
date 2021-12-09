
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from config import base_path
from hh_bot import search_all_vacancies_by_resume, get_formatted_vacancy
from base.basemanage import UserManage, ResumesManage, VacancyManage
from config import hh_user_access_token as hh_token
from config import resume_ids


def create_session(base_path):
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def get_new_vacancies(access_token, resume_id, session):

    vacancies_list = search_all_vacancies_by_resume(access_token, resume_id)
    vacancies_in_base = session.query(Vacancies).order_by(Vacancies.id).all()[::-1]

    for vacancy in vacancies_list.copy():
        for vacancy_in_base in vacancies_in_base:
            if vacancy['alternate_url'] is vacancy_in_base.url:
                vacancy_in_base.remove(vacancy_in_base)
                vacancies_list.remove(vacancy)
                break

    if not vacancies_list:
        return None

    return vacancies_list


def add_vacancies_to_base(vacancies_list, session):

    for vacancy in vacancies_list:
        try:
            session.add(Vacancies(*get_formatted_vacancy(vacancy)))
            session.commit()
        except IntegrityError:
            session.rollback()


if __name__ == "__main__":
    session = create_session(base_path)

    new_vacancies = []
    for resume_id in resume_ids:
        new_vacancies.extend(get_new_vacancies(hh_token, resume_id, session))

    add_vacancies_to_base(new_vacancies, session)
