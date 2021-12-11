import time
from base.basemanage import ResumesManage, UserManage
from hh_bot import publish_resume, refresh_access_token
from config import userbase_path

resumes = ResumesManage.get_all_resumes(userbase_path)

time_now = time.time()
for resume in resumes:
    if resume.resume.autoupdate:
        if time_now > resume.resume.user.hh_acc_token_exp.timestamp():
            user = UserManage(userbase_path, resume.resume.user.id)
            new_token_data = refresh_access_token(resume.resume.user.hh_refresh_token)
            user.set_user_tokens(new_token_data['access_token'],
                                 new_token_data['refresh_token'],
                                 new_token_data['expires_in'])

        publish_resume(resume.resume.user.hh_access_token, resume.resume.resume_id)
