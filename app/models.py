# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb import EndpointsModel


class CommentModel(EndpointsModel):
    content = ndb.TextProperty(required=True)
    when = ndb.DateTimeProperty(auto_now_add=True)
    user_id = ndb.IntegerProperty()
    author = ndb.StringProperty()
    category = ndb.StringProperty()
    organization_id = ndb.IntegerProperty()
    complain = ndb.BooleanProperty(default=False)
    rude = ndb.BooleanProperty(default=False)
    task = ndb.BooleanProperty(default=False)
    done = ndb.BooleanProperty(default=False)
    from_contacts = ndb.BooleanProperty(default=False)


class OrganizationModel(EndpointsModel):
    category = ndb.StringProperty(default=u'Другие')
    title = ndb.StringProperty(default=u'Без названия')
    location = ndb.GeoPtProperty()
    adres = ndb.StringProperty()
    adres_details = ndb.StringProperty()
    phonenumber = ndb.StringProperty(repeated=True)
    phonenumber_static = ndb.StringProperty(repeated=True)
    rating = ndb.IntegerProperty(default=0)
    when_added = ndb.DateTimeProperty(auto_now_add=True)
    when_modified = ndb.DateTimeProperty(auto_now=True)
    author = ndb.StringProperty()
    owner = ndb.StringProperty()
    description = ndb.TextProperty()
    tags = ndb.StringProperty(repeated=True)
    price = ndb.IntegerProperty(default=0)
    size = ndb.IntegerProperty(default=2)
    delivery_terms = ndb.StringProperty()
    working_hours = ndb.StringProperty()
    assortiment = ndb.PickleProperty()
    internet_site = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()  # to add
    daynight = ndb.BooleanProperty(default=False)
    high_quality = ndb.BooleanProperty(default=False)  # to add
    delivery = ndb.BooleanProperty(default=False)
    new = ndb.BooleanProperty(default=False)


class UserModel(EndpointsModel):
    google_user = ndb.UserProperty()
    email = ndb.StringProperty()
    email_confirmed = ndb.BooleanProperty(default=False)
    email_confirmed_on = ndb.DateTimeProperty()
    nickname = ndb.StringProperty()
    password = ndb.StringProperty()
    when_came = ndb.DateTimeProperty(auto_now_add=True)
    last_seen = ndb.DateTimeProperty(auto_now_add=True)
    visits = ndb.IntegerProperty()
    modifications = ndb.IntegerProperty()
    contributions = ndb.IntegerProperty()
    false_actions = ndb.IntegerProperty()
    rating = ndb.IntegerProperty()
    vk_access_token = ndb.StringProperty()
    vk_user_id = ndb.IntegerProperty()
    vk_expires_in = ndb.IntegerProperty()
    ok_user_id = ndb.IntegerProperty()
    ok_access_token = ndb.StringProperty()
    wot_access_token = ndb.StringProperty()
    wot_account_id = ndb.StringProperty()
    is_authenticated = ndb.BooleanProperty(default=True)
    is_active = ndb.BooleanProperty(default=True)
    is_anonymous = ndb.BooleanProperty(default=False)
    is_admin = ndb.BooleanProperty(default=False)
    liked_orgs = ndb.IntegerProperty(repeated=True)

    def get_id(self):
        return self.key.id()


class TagsModel(EndpointsModel):
    all_tags = ndb.StringProperty(repeated=True)
    uid = ndb.StringProperty()


# Count search words
class SearchWordsModel(EndpointsModel):
    word = ndb.StringProperty()
    quantity = ndb.IntegerProperty()
