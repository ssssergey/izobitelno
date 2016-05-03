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

vk_app_id = "5437643"
vk_client_secret = "BZMjgoDhd8lW4iIVw5hC"
ok_app_id = "1246901248"
ok_app_key = "CBAFDDFLEBABABABA"
ok_app_secret = "6F1192E1F73E17EFE7E00DC4"