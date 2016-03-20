# -*- coding: utf-8 -*-
import json
from datetime import datetime
from collections import OrderedDict
from flask import render_template, redirect, flash, url_for, request
from app import app
from models import PostModel, OrganizationModel, TagsModel
from decorators import login_required
from google.appengine.api import users, datastore_types
from google.appengine.ext import ndb
from google.appengine.api import memcache
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired,Length,EqualTo

categories = [
    {'eng_title':'food',
    'rus_title':u'Еда',
    'icon':"fa fa-cutlery fa-fw",
    'categs':{'beer':u'Пиво','pizza':u'Пицца','meat':u'Мясо','fish':u'Рыба','vegets_fruits':u'Овощи и фрукты',
              'food_shop':u'Продуктовый магазин','dining':u'Столовая'}},
    {'eng_title':'auto',
    'rus_title':u'Авто',
     'icon':"fa fa-car fa-fw",
    'categs':{'autowash':u'Автомойка','autopaint':u'Автопокраска','autoglass':u'Автостекло','autotyres':u'Шиномонтаж',
              'autoshop':u'Автозапчасти','motoroil_change':u'Замена моторного масла', 'chassis':u'Ходовая',
              'electric':u'Электрик','osago':u'ОСАГО','gasstation':u'АЗС'}},
    {'eng_title':'service',
    'rus_title':u'Бытовые услуги',
     'icon':"fa fa-group fa-fw",
    'categs':{'hair':u'Парикмахерская', 'atelye':u'Ателье', 'grugstore':u'Аптека', 'photo':u'Фото',
              'repair_gadgets':u'Ремонт техники','salon':u'Салон красоты'}},
    {'eng_title':'house',
    'rus_title':u'Для дома',
     'icon':"glyphicon glyphicon-home",
    'categs':{'construction':u'Строительный магазин', 'garden':u'Сад и огород', 'furniture':u'Мебель', 'security':u'Системы безопасности'}},
    {'eng_title':'finance_state',
    'rus_title':u'Финансовые и госслужбы',
     'icon':"fa fa-bank fa-fw",
    'categs':{'sbercashpoint':u'Банкомат Сбербанка', 'bank':u'Банк', 'state_service':u'Госуслуги'}},
    {'eng_title':'goods',
    'rus_title':u'Бытовые товары',
     'icon':"fa fa-tablet fa-fw",
    'categs':{'pc':u'Компьютеры и комплектующие', 'smarphones':u'Телефоны'}},
    {'eng_title':'leisure',
    'rus_title':u'Досуг',
     'icon':"glyphicon glyphicon-send",
    'categs':{'gym':u'Тренажерный (фитнес) зал', 'running':u'Бег', 'cafe_bar':u'Кафе и бары', 'banya':u'Баня и сауна',
              'billiards':u'Бильярд', 'fishing_hunting':u'Рыбалка и охота' }},
    {'eng_title':'children',
    'rus_title':u'Дети',
     'icon':"fa fa-child fa-fw",
    'categs':{'kindergarden':u'Детсад', 'childgoods':u'Товары для детей'}, 'developement':u'Развитие'},
    {'eng_title':'accommodation',
    'rus_title':u'Жилье',
     'icon':"fa fa-bed fa-fw",
    'categs':{'hotel':u'Гостиница', 'private':u'Частники'}},
    {'eng_title':'celebration',
    'rus_title':u'На праздник',
     'icon':"fa fa-birthday-cake fa-fw",
    'categs':{'flowers':u'Цветы', 'fireworks':u'Фейерверки', 'celebration_goods':u'Товары для праздника'}},
    ]
categories_callable = [{'eng_title':'callable',
                        'rus_title':u'Вызов на дом',
                        'icon':"fa fa-phone fa-fw",
                        'citaton':(u'', u''),
                        'categs':{'taxi':u'Такси','pizza':u'Пицца', 'electric':u'Электрик', 'plummer':u'Сантехник',
                                  'nanny':u'Няня','gasmaster':u'Газовщик','hodman':u'Подсобный','cargo':u'Грузоперевозки'}},
                       ]
categories_all = {}
for i_dict in categories:
    categories_all.update(i_dict['categs'])
for i_dict in categories_callable:
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
    tags = StringField()


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
    all_tags = get_all_tags()
    return render_template("index.html", categories=categories, categories_callable=categories_callable, all_tags=','.join(all_tags))

@app.route('/search', methods = ['GET', 'POST'])
def search():
    keyword = request.form.get('search').lower()
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == keyword).fetch()
    return render_template("search_result.html", posts = json.loads(json.dumps(selected_orgs, cls=GaeEncoder)))

@app.route('/category/<category_eng>')
def category(category_eng):
    orgs = OrganizationModel.query(OrganizationModel.category == categories_all[category_eng]).fetch()
    return render_template("category_with_map.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)),
                           category_rus=categories_all[category_eng], category_eng=category_eng, categories=categories,
                           categories_callable=categories_callable)

@app.route('/orgs/new', methods = ['GET', 'POST'])
def new_org():
    category = request.args.get("category_value")
    orgs = OrganizationModel.query(OrganizationModel.category == category).fetch()
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
                                tags = form.tags.data.split(',')
                                 )
        post.put()
        flash(u'Организация успешно добавлена!')
        for eng, rus in categories_all.iteritems():
            if rus == form.category.data:
                category_eng = eng
        add_tag(form.tags.data.lower().split(','))
        return redirect(url_for('category', category_eng=category_eng))
    all_tags = get_all_tags()
    return render_template('new_org.html', form=form, categories=categories, posts = json.loads(json.dumps(orgs, cls=GaeEncoder)), all_tags=','.join(all_tags))

@app.route('/edit_org/<int:id>', methods = ['GET', 'POST'])
def edit_org(id):
    org = OrganizationModel.get_by_id(int(id))
    if users.is_current_user_admin() or users.get_current_user() == org.author:
        form = OrganizationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
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
                            tags = form.tags.data.split(',')
                             )
                org.put()
                flash(u'Изменения приняты!')
                for eng, rus in categories_all.iteritems():
                    if rus == form.category.data:
                        category_eng = eng
                add_tag(form.tags.data.lower().split(','))
                return redirect(url_for('category', category_eng=category_eng))
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
        form.tags.data = ",".join(org.tags)
        orgs = OrganizationModel.query(OrganizationModel.category == org.category).fetch()
        all_tags = get_all_tags()
        return render_template("edit_org.html", form=form, id=id, posts = json.loads(json.dumps(orgs, cls=GaeEncoder)), tags=",".join(org.tags), all_tags=','.join(all_tags))
    else:
        flash(u"У вас нет права на редактирование. Вы не являетесь автором этого объекта!")
        for eng, rus in categories_all.iteritems():
            if rus == org.category:
                category_eng = eng
        return redirect(url_for('category', category_eng=category_eng))


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

def add_tag(tag_list):
    new_list = []
    tags_from_ds = TagsModel.query(TagsModel.uid == 'myid').get()
    # Если нет такой записи,то создаем ее
    if not tags_from_ds:
        tags_from_ds = TagsModel(uid='myid')
    old_list = tags_from_ds.all_tags
    new_list = list(set(old_list+tag_list))
    memcache.set('all_tags', new_list)
    tags_from_ds.all_tags = new_list
    tags_from_ds.put()

def get_all_tags(update=False):
    all_tags = memcache.get('all_tags')
    if all_tags is None or update:
        all_tags = TagsModel.query(TagsModel.uid == 'myid').get()
        if all_tags:
            all_tags = all_tags.all_tags
            memcache.set('all_tags', all_tags)
        else:
            all_tags = []
    return all_tags

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
