# -*- coding: utf-8 -*-
import json
from datetime import datetime
from collections import OrderedDict
from flask import render_template, redirect, flash, url_for, request
from app import app
from models import PostModel, OrganizationModel
from decorators import login_required
from google.appengine.api import users, datastore_types
from google.appengine.ext import ndb

from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired,Length,EqualTo

categories = [
    {'eng_title':'food',
    'rus_title':u'Еда',
    'icon':"fa fa-cutlery fa-fw",
    'categs':{'beer':u'Пиво','pizza':u'Пицца','meat':u'Мясо','fish':u'Рыба','vegets_fruits':u'Овощи и фрукты',
              'water':u'Вода для кулеров'}},
    {'eng_title':'auto',
    'rus_title':u'Авто',
     'icon':"fa fa-car fa-fw",
    'categs':{'autowash':u'Автомойка','autopaint':u'Автопокраска','autoglass':u'Автостекло','autotyres':u'Шиномонтаж',
              'motoroil_buy':u'Купить моторное масло','motoroil_change':u'Замена моторного масла', 'chassis':u'Ходовая',
              'electric':u'Электрик','osago':u'ОСАГО'}},
    {'eng_title':'service',
    'rus_title':u'Бытовые услуги',
     'icon':"fa fa-group fa-fw",
    'categs':{'hair':u'Парикмахерская', 'atelye':u'Ателье', 'grugstore':u'Аптека'}},
    {'eng_title':'house',
    'rus_title':u'Для дома',
     'icon':"fa fa-bank fa-fw",
    'categs':{'construction':u'Строительный магазин', 'garden':u'Сад и огород'}},
    {'eng_title':'finance',
    'rus_title':u'Банки и финансы',
     'icon':"fa fa-dollar fa-fw",
    'categs':{'sbercashpoint':u'Банкомат Сбербанка', 'bank':u'Банк'}},
    {'eng_title':'gadget',
    'rus_title':u'Компьютеры и гаджеты',
     'icon':"fa fa-tablet fa-fw",
    'categs':{'pc':u'Компьютеры и комплектующие', 'smarphones':u'Телефоны', 'repair_gadgets':u'Ремонт'}},
    {'eng_title':'sport',
    'rus_title':u'Спорт',
     'icon':"fa fa-futbol-o fa-fw",
    'categs':{'gym':u'Тренажерный (фитнес) зал', 'running':u'Бег'}},
    ]
categories_all = {}
for i_dict in categories:
    categories_all.update(i_dict['categs'])


class OrganizationForm(Form):
    category = StringField()
    title = StringField(default=u"Без названия")
    adres = StringField()
    phonenumber = StringField(render_kw={"placeholder": u"+7 928 1111111"})
    rating = IntegerField(default=0)
    owner = StringField(render_kw={"placeholder": u"дядя Коля"})
    lat = FloatField()
    lng = FloatField()
    description = TextAreaField()


class GaeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return (obj - datetime(1970,1,1)).total_seconds()
        elif isinstance(obj, ndb.Model):
            result = obj.to_dict()
            result['id'] = obj.key.id()
            return result
        elif isinstance(obj, users.User):
            return obj.nickname()
        elif isinstance(obj, datastore_types.GeoPt):
            return {'lat': obj.lat, 'lng':obj.lon}
        else:
            return json.JSONEncoder.default(self, obj)


@app.route('/')
def index():
    return render_template("index.html", categories=categories)

@app.route('/category/<category_eng>')
def category(category_eng):
    orgs = OrganizationModel.query(OrganizationModel.category == categories_all[category_eng]).fetch()
    return render_template("category_with_map.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)),
                           category_rus=categories_all[category_eng], category_eng=category_eng, categories=categories)

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
                                author = users.get_current_user(),
                                user_modified = users.get_current_user(),
                                description = form.description.data,
                                 )
        post.put()
        flash(u'Организация успешно добавлена!')
        for eng, rus in categories_all.iteritems():
            if rus == form.category.data:
                category_eng = eng
        return redirect(url_for('category', category_eng=category_eng))
    return render_template('new_org.html', form=form, categories=categories)

@app.route('/edit_org/<int:id>', methods = ['GET', 'POST'])
def edit_org(id):
    form = OrganizationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            org = OrganizationModel.get_by_id(int(id))
            org.populate(title = form.title.data,
                        category = form.category.data,
                        phonenumber = form.phonenumber.data,
                        rating = form.rating.data,
                        owner = form.owner.data,
                        adres = form.adres.data,
                        location = ndb.GeoPt(form.lat.data, form.lng.data),
                        user_modified = users.get_current_user(),
                        when_modified = datetime.now(),
                        description = form.description.data,
                         )
            org.put()
            flash(u'Изменения приняты!')
            for eng, rus in categories_all.iteritems():
                if rus == form.category.data:
                    category_eng = eng
            return redirect(url_for('category', category_eng=category_eng))
    org = OrganizationModel.get_by_id(int(id))
    form = OrganizationForm()
    form.category.data = org.category
    form.title.data = org.title
    form.phonenumber.data = org.phonenumber
    form.rating.data = org.rating
    form.owner.data = org.owner
    form.adres.data = org.adres
    form.description.data = org.description
    form.lat.data = org.location.lat
    form.lng.data = org.location.lon
    return render_template("edit_org.html", form=form, id=id)

@app.route('/del_org/<int:id>', methods = ['GET','DELETE'])
def del_org(id):
    org = OrganizationModel.get_by_id(int(id))
    current_user = users.get_current_user()
    for eng, rus in categories_all.iteritems():
        if rus == org.category:
            category_eng = eng
    if users.is_current_user_admin():
        flash(u"Вы успешно удалили объект как администратор!")
        org.key.delete()
        return redirect(url_for('category', category_eng=category_eng))
    if current_user == org.author:
        flash(u"Вы успешно удалили объект как автор!")
        org.key.delete()
        return redirect(url_for('category', category_eng=category_eng))
    else:
        flash(u"У вас нет права на удаление. Вы не являетесь автором этого объекта!")
        return redirect(url_for('category', category_eng=category_eng))


@app.route('/orgs')
def list_orgs():
    orgs = OrganizationModel.query().order(-OrganizationModel.when_added)
    return render_template('list_orgs.html', posts=orgs, categories=categories)




@app.route('/contacts')
def contacts():
    return render_template("contacts.html", categories=categories)

@app.route('/traffic')
def traffic():
    return render_template("traffic.html", categories=categories)

@app.route('/location')
def location():
    return render_template("location.html")

######## POST ###########
class PostForm(Form):
    content = TextAreaField('Content', validators=[DataRequired()])

@app.route('/posts')
def list_posts():
    posts = PostModel.query().order(-PostModel.when)
    return render_template('list_posts.html', posts=posts, categories=categories)

@app.route('/posts/new', methods = ['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = PostModel(
                    content = form.content.data,
                    author = users.get_current_user())
        post.put()
        flash(u'Комментарий успешно создан!')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html', form=form, categories=categories)
