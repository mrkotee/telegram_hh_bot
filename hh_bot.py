import requests


def get_app_token(client_id, client_secret):
    url = 'https://hh.ru/oauth/token'
    data = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        print('Bad request')
    elif response.status_code == 403:
        print("Too often requests")
    return False


def create_auth_url(client_id, user_id, redirect_uri):
    """

    :param client_id: hh app id
    :param user_id: tg chat id
    :param redirect_uri: uri to redirect from hh after authorization
    :return: url for authorization
    """
    # url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}'
    ## create redirect page on flask! and when url be:
    url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}&state={user_id}'\
        f'&redirect_uri={redirect_uri}'
    return url


def get_user_access_token(client_id, client_secret, user_code):
    """
    :return: (
        access_token,
        refresh_token,
        access_token_expires_in
    )
    """
    url = 'https://hh.ru/oauth/token'
    data = f"code={user_code}&client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        res_json = response.json()
        return res_json['access_token'], res_json['refresh_token'], res_json['expires_in']
    elif response.status_code == 400:
        print('Bad request')
    return False


def refresh_access_token(refresh_token):
    """
    :return: {
        "access_token": "{access_token}",
        "token_type": "bearer",
        "expires_in": 1209600,
        "refresh_token": "{refresh_token}"
        }
    """
    url = 'https://hh.ru/oauth/token'
    data = f"refresh_token={refresh_token}&grant_type=refresh_token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        print('Bad request')
    return False


def check_token(access_token):
    """check user access token
    :return user's json if token is active
    :return False if not
    :return None if data incorrect"""
    url = "https://api.hh.ru/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        return False

    return None


def get_user_resumes(access_token):
    """

    :param access_token: hh access_token
    :return: dict {resume_id: resume_title}
    """
    url = f'https://api.hh.ru/resumes/mine'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    return {resume['id']: resume['title'] for resume in response.json()['items']}


def publish_resume(access_token, resume_id):
    url = f'https://api.hh.ru/resumes/{resume_id}/publish'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.post(url, headers=headers)

    if response.status_code == 204:
        return True
    elif response.status_code == 400:
        print('Bad request')
    return False


def get_resume_title(access_token, resume_id):
    url = f'https://api.hh.ru/resumes/{resume_id}'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return response.json()['title']
    elif response.status_code == 400:
        print('Bad request')
    return False


def get_resume_url(hh_resume_id):
    return f"https://hh.ru/resume/{hh_resume_id}"


def search_vacancies_by_resume(access_token, resume_id, page=0, per_page=40):
    headers = {'Authorization': 'Bearer ' + access_token}
    url = f"https://api.hh.ru/resumes/{resume_id}/similar_vacancies"
    url += f'?page={page}&per_page={per_page}'

    response = requests.get(url, headers=headers)

    if response.status_code == 400:
        print("Bad request")
        return False
    elif response.status_code == 404:
        print("Resume not found")
        return False

    result_json = response.json()
    return result_json['items'], result_json['page'], result_json['per_page'], result_json['pages'],


def search_all_vacancies_by_resume(access_token, resume_id):

    vacancies_list = []
    pages_info = [-1, 99, 99]  # -1 because first page is "0"
    while pages_info[0] < pages_info[2]-1: # cur_page < pages_at_all
        finded_vacancies, *pages_info = search_vacancies_by_resume(access_token, resume_id, page=pages_info[0]+1)
        vacancies_list.extend(finded_vacancies)

    return vacancies_list


def get_formatted_vacancy(vacancy_dict):
    def try_to_get_value(value_dict, key_list):
        value = value_dict
        for key in key_list:
            try:
                value = value[key]
            except TypeError:
                return ''
        return value

    name = try_to_get_value(vacancy_dict, ['name'])
    salary = 'salary from *' + str(try_to_get_value(vacancy_dict, ['salary', 'from']))\
             + '* to *' + str(try_to_get_value(vacancy_dict, ['salary', 'to'])) + '*'
    vacancy_url = try_to_get_value(vacancy_dict, ['alternate_url'])
    company = try_to_get_value(vacancy_dict, ['employer', 'name'])
    created_at = try_to_get_value(vacancy_dict, ['created_at'])
    requir = try_to_get_value(vacancy_dict, ['snippet', 'requirement'])
    resposib = try_to_get_value(vacancy_dict, ['snippet', 'responsibility'])
    metrostation = try_to_get_value(vacancy_dict, ['address', 'metro', 'station_name'])

    description = '{}\nCompany: *{}*\nRequirements: {}\nResponsibility: {}\nCreated: {}\nStation: {}\n'.format(
        salary, company, requir, resposib, created_at, metrostation)

    return vacancy_url, name, description


def filter_vacancies_by_keyword(vacancies_list, keyword):
    result_list = []
    if isinstance(vacancies_list[0], dict):
        for vacancy in vacancies_list:
            for v in vacancy.values():
                if keyword.lower() in v.lower():
                    result_list.append(vacancy)

    elif isinstance(vacancies_list[0], tuple) or isinstance(vacancies_list, list):
        for vacancy in vacancies_list:
            for v in vacancy:
                if keyword.lower() in v.lower():
                    result_list.append(vacancy)
                    break

    return result_list

