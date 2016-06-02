# -*- coding: utf-8 -*-
import os
from secret import *

DEBUG=True
SECRET_KEY=secret_key
SECURITY_PASSWORD_SALT = security_password_salt
CSRF_ENABLED=True
CSRF_SESSION_LKEY=csrf_session_lkey

# main config
BCRYPT_LOG_ROUNDS = 13
WTF_CSRF_ENABLED = True
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

# mail settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# gmail authentication
# MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
MAIL_USERNAME = mail_username
# MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']
MAIL_PASSWORD = mail_password

# mail accounts
MAIL_DEFAULT_SENDER = 'from@example.com'

vk_app_id = vk_app_id_S
vk_client_secret = vk_client_secret_S
ok_app_id = ok_app_id_S
ok_app_key = ok_app_key_S
ok_app_secret = ok_app_secret_S