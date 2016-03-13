from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb import EndpointsModel

class PostModel(ndb.Model):
    title = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    when = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty(required = True)

class OrganizationModel(EndpointsModel):
    category = ndb.StringProperty()
    title = ndb.StringProperty(required = True)
    location = ndb.GeoPtProperty()
    adres = ndb.StringProperty()
    phonenumber = ndb.StringProperty()
    rating = ndb.StringProperty()
    when_added = ndb.DateTimeProperty(auto_now_add = True)
    when_modified = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty()
    owner = ndb.StringProperty()

class UserModel(ndb.Model):
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

