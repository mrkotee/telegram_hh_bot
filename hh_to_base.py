import time
from config import base_path, userbase_path
from hh_bot import search_all_vacancies_by_resume, get_formatted_vacancy, refresh_access_token
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
        try:
            vacancy_m.add_vacancy(*get_formatted_vacancy(vacancy),
                              resume_id=resume.resume.id, user_id=user.user.id)
        except Exception as e:
            print(vacancy, e)


if __name__ == "__main__":
    users = UserManage.get_all_users(userbase_path)
    time_now = time.time()
    for user in users:
        resumes_ids = user.get_all_user_resumes_id()
        for resume_id in resumes_ids:
            resume = ResumesManage(userbase_path, resume_id)
            if not resume.active:
                continue
            try:
                if time_now > resume.resume.user.hh_acc_token_exp.timestamp():
                    user = UserManage(userbase_path, resume.resume.user.id)
                    new_token_data = refresh_access_token(resume.resume.user.hh_refresh_token)
                    user.set_user_tokens(new_token_data['access_token'],
                                         new_token_data['refresh_token'],
                                         new_token_data['expires_in'])
                new_vacancies = get_new_vacancies(user.get_user_access_token(), resume, base_path)
                if new_vacancies:
                    add_vacancies_to_base(new_vacancies, base_path, resume, user)
            except Exception as e:
                print("user id ", user.user.id, "resume id ", resume_id, e)
                continue
