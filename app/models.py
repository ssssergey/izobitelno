# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb import EndpointsModel

class PostModel(EndpointsModel):
    content = ndb.TextProperty(required = True)
    when = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty(required = True)
    category = ndb.StringProperty()
    organization_id = ndb.IntegerProperty()

class OrganizationModel(EndpointsModel):
    category = ndb.StringProperty(default=u'Другие')
    title = ndb.StringProperty(default=u'Без названия')
    location = ndb.GeoPtProperty()
    adres = ndb.StringProperty()
    phonenumber = ndb.StringProperty(repeated=True)
    phonenumber_static = ndb.StringProperty(repeated=True)
    rating = ndb.IntegerProperty()
    when_added = ndb.DateTimeProperty(auto_now_add = True)
    when_modified = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty(required = True)
    user_modified = ndb.UserProperty()
    owner = ndb.StringProperty()
    description = ndb.TextProperty()
    tags = ndb.StringProperty(repeated=True)

class UserModel(EndpointsModel):
    auth_object = ndb.UserProperty(required = True)
    nickname = ndb.StringProperty(required = True)
    password = ndb.StringProperty()
    when_added = ndb.DateTimeProperty(auto_now_add = True)
    when_last_visit = ndb.DateTimeProperty(auto_now_add = True)
    visits = ndb.IntegerProperty()
    modifications = ndb.IntegerProperty()
    contributions = ndb.IntegerProperty()
    incorrect_actions = ndb.IntegerProperty()
    false_actions = ndb.IntegerProperty()
    rating = ndb.IntegerProperty()

class TagsModel(EndpointsModel):
    all_tags = ndb.StringProperty(repeated=True)
    uid = ndb.StringProperty()
