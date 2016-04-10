# -*- coding: utf-8 -*-
import re
from flask import Flask
import settings
from jinja2 import evalcontextfilter, Markup, escape
from momentjs import momentjs

app = Flask(__name__)

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


app.jinja_env.globals['momentjs'] = momentjs


app.config.from_object('app.settings')

import views