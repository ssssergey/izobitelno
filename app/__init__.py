# -*- coding: utf-8 -*-
from flask import Flask
import settings

app = Flask(__name__)
app.config.from_object('app.settings')

import views