# -*- coding: utf-8 -*-
from jinja2 import Markup
from datetime import datetime

class momentjs(object):
    def __init__(self, timestamp):
        if isinstance(timestamp, float):
            timestamp = datetime.utcfromtimestamp(timestamp)
        self.timestamp = timestamp

    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")