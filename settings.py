# -*- coding: utf-8 -*-
import os

DEBUG=True
SECRET_KEY='dev_key_h8hfne89vm'
SECURITY_PASSWORD_SALT = 'sljgajie99gwtjwi3jlgklsgmslijseilgh'
CSRF_ENABLED=True
CSRF_SESSION_LKEY='dev_key_h8asSNJ9s9=+'

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
MAIL_USERNAME = 'izopoisk@gmail.com'
# MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']
MAIL_PASSWORD = 'secret_password'

# mail accounts
MAIL_DEFAULT_SENDER = 'from@example.com'