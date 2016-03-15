# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import render_template, redirect, flash, url_for
from app import app
from models import PostModel, OrganizationModel
from decorators import login_required
from google.appengine.api import users, datastore_types
from google.appengine.ext import ndb

from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired,Length,EqualTo

class OrganizationForm(Form):
    category = StringField(render_kw={"placeholder": u"Пиво"})
    title = StringField(render_kw={"placeholder": u"МегаПиво"})
    adres = StringField(render_kw={"placeholder": u"ул. Ленина, 10"})
    phonenumber = StringField(render_kw={"placeholder": u"+7 928 1231212"})
    rating = IntegerField(render_kw={"placeholder": u"+7 928 1231212"})
    owner = StringField(render_kw={"placeholder": u"дядя Коля"})
    lat = FloatField()
    lng = FloatField()

@app.route('/orgs')
def list_orgs():
    orgs = OrganizationModel.query()
    return render_template('list_orgs.html', posts=orgs)

@app.route('/orgs/new', methods = ['GET', 'POST'])
def new_org():
    form = OrganizationForm()
    if form.validate_on_submit():
        post = OrganizationModel(title = form.title.data,
                    category = form.category.data,
                    phonenumber = form.phonenumber.data,
                    rating = form.rating.data,
                    owner = form.owner.data,
                    adres = form.adres.data,
                    location = ndb.GeoPt(form.lat.data, form.lng.data),
                    author = users.get_current_user())
        post.put()
        flash('Organization saved on database.')
        return redirect(url_for('list_orgs'))
    return render_template('new_org.html', form=form)

class GaeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return (obj - datetime(1970,1,1)).total_seconds()
        elif isinstance(obj, ndb.Model):
            return obj.to_dict()
        elif isinstance(obj, users.User):
            return obj.nickname()
        elif isinstance(obj, datastore_types.GeoPt):
            return {'lat': obj.lat, 'lng':obj.lon}
        else:
            return json.JSONEncoder.default(self, obj)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/pizza')
def pizza():
    orgs = OrganizationModel.query(OrganizationModel.category == u'Пицца').fetch()
    return render_template("pizza.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)))

@app.route('/beer')
def beer():
    orgs = OrganizationModel.query(OrganizationModel.category == u'Пиво').fetch()
    return render_template("beer.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)))

@app.route('/contacts')
def contacts():
    return render_template("contacts.html")

@app.route('/traffic')
def traffic():
    return render_template("traffic.html")

@app.route('/location')
def location():
    return render_template("location.html")

######## POST ###########
class PostForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

@app.route('/posts')
def list_posts():
    posts = PostModel.query()
    return render_template('list_posts.html', posts=posts)

@app.route('/posts/new', methods = ['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = PostModel(title = form.title.data,
                    content = form.content.data,
                    author = users.get_current_user())
        post.put()
        flash('Post saved on database.')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html', form=form)
