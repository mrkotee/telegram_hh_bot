
from config import base_path, userbase_path
from hh_bot import search_all_vacancies_by_resume, get_formatted_vacancy
from base.basemanage import UserManage, ResumesManage, VacancyManage


def get_new_vacancies(access_token, resume, vacancy_base_path):
    vacancies_list = search_all_vacancies_by_resume(access_token, resume.resume.resume_id)
    vacancies_in_base = VacancyManage(vacancy_base_path).get_all_vacancies_by_resume(resume.resume.id)

    for vacancy in vacancies_list.copy():
        for vacancy_in_base in vacancies_in_base:
            if vacancy['alternate_url'] == vacancy_in_base.url:
                vacancies_in_base.remove(vacancy_in_base)
                vacancies_list.remove(vacancy)
                break

    if not vacancies_list:
        return None

    return vacancies_list


def add_vacancies_to_base(vacancies_list, vacancy_base_path, resume, user):
    vacancy_m = VacancyManage(vacancy_base_path)
    for vacancy in vacancies_list:
        vacancy_m.add_vacancy(*get_formatted_vacancy(vacancy),
                              resume_id=resume.resume.id, user_id=user.user.id)


if __name__ == "__main__":
    users = UserManage.get_all_users(userbase_path)
    for user in users:
        resumes_ids = user.get_all_user_resumes_id()
        for resume_id in resumes_ids:
            resume = ResumesManage(userbase_path, resume_id)
            if not resume.active:
                continue
            new_vacancies = get_new_vacancies(user.get_user_access_token(), resume, base_path)
            if new_vacancies:
                add_vacancies_to_base(new_vacancies, base_path, resume, user)
