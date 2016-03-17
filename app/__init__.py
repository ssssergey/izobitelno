# -*- coding: utf-8 -*-
from flask import Flask
import settings
from momentjs import momentjs

app = Flask(__name__)
app.jinja_env.globals['momentjs'] = momentjs

app.config.from_object('app.settings')

import views