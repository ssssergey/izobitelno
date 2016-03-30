# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import render_template, redirect, flash, url_for, request, jsonify
from app import app
from models import PostModel, OrganizationModel, TagsModel
from google.appengine.api import users, datastore_types
from google.appengine.ext import ndb
from google.appengine.api import memcache
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, IntegerField, BooleanField, widgets
from wtforms.validators import DataRequired,NumberRange

categories = [
    {'eng_title':'food',
    'rus_title':u'Еда',
    'icon':"fa fa-cutlery fa-fw",
    'categs':{'beer':u'Пиво разливное','pizza':u'Пицца','meat':u'Мясо','fish':u'Рыба','vegets_fruits':u'Овощи и фрукты',
              'food_shop':u'Продуктовый магазин','dining':u'Столовая','alcohol':u'Алкоголь','sweets':u'Сладости'}},
    {'eng_title':'auto',
    'rus_title':u'Авто',
    'icon':"fa fa-car fa-fw",
    'categs':{'autowash':u'Автомойка','autopaint':u'Автопокраска','autotyres':u'Шиномонтаж',
              'autoshop':u'Автозапчасти','sto':u'СТО','osago':u'ОСАГО','gasstation':u'АЗС'}},
    {'eng_title':'service',
    'rus_title':u'Услуги',
    'icon':"fa fa-group fa-fw",
    'categs':{'atelye':u'Ателье', 'photo':u'Фото', 'repair_gadgets':u'Ремонт вещей',
              'salon':u'Салон красоты','sbercashpoint':u'Банкомат Сбербанка',
              'bank':u'Банк', 'state_service':u'Госуслуги','hotel':u'Гостиница',
              'kindergarden':u'Детсад', 'child_developement':u'Развитие детей', 'toilet':u'Туалет',
              'service_charge':u'Оплата услуг','jurist':u'Юридические','health':u'Здоровье'}},
    {'eng_title':'goods',
    'rus_title':u'Товары',
    'icon':"glyphicon glyphicon-home",
    'categs':{'construction':u'Строительный магазин', 'garden':u'Сад и огород', 'furniture':u'Мебель', 'security':u'Безопасность',
             'gadgets':u'Электроника', 'fishing_hunting':u'Рыбалка и охота','childgoods':u'Товары для детей','flowers':u'Цветы',
             'grugstore':u'Аптека','officeshop':u'Канцелярский магазин','clothes':u'Одежда','household_goods':u'Бытовые товары',
                'celebration':u'Праздничные','animals':u'Животным','ritual':u'Ритуальные','textile':u'Текстиль'}},
    {'eng_title':'leisure',
    'rus_title':u'Досуг',
    'icon':"glyphicon glyphicon-send",
    'categs':{'gym':u'Тренажерный (фитнес) зал', 'running':u'Бег', 'cafe_bar':u'Кафе и бары', 'banya':u'Баня и сауна',
              'team_sport':u'Командный спорт','billiards':u'Бильярд'}},
    ]

categories_callable = [{'eng_title':'callable',
                        'rus_title':u'Вызов на дом',
                        'icon':"fa fa-phone fa-fw",
                        'citaton':(u'', u''),
                        'categs':{'taxi':u'Такси','pizza':u'Пицца', 'electric':u'Электрик', 'plummer':u'Сантехник',
                                  'nanny':u'Няня','gasmaster':u'Газовщик','hodman':u'Подсобный','cargo':u'Грузоперевозки',
                                  'others':u'Прочее','building':u'Ремонт и строительство'}},
                       ]
categories_all = {}
for i_dict in categories:
    categories_all.update(i_dict['categs'])
for i_dict in categories_callable:
    categories_all.update(i_dict['categs'])

class OrganizationForm(Form):
    category = StringField()
    title = StringField(default=u"Без названия")
    adres = StringField(default=u"")
    phonenumber = StringField(widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"(999) 999-9999"})
    phonenumber_static = StringField(widget=widgets.Input(input_type="tel"),render_kw={"placeholder": u"9-99-99"})
    rating = IntegerField(widget=widgets.Input(input_type="tel"),default=0)
    owner = StringField(render_kw={"placeholder": u"Иван Иванович"})
    lat = FloatField(default=0)
    lng = FloatField(default=0)
    description = TextAreaField()
    tags = StringField()
    price = IntegerField(widget=widgets.Input(input_type="tel"),default=0)
    size = IntegerField(u'Размер объекта(1-5)', widget=widgets.Input(input_type="tel"),default=2, validators=[NumberRange(message=u'От 1 до 5', min=1, max=5)])
    quality = BooleanField(default=False)

class GaeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return (obj - datetime(1970,1,1)).total_seconds()
        # elif isinstance(obj, list):
        #     return ', '.join([i for i in obj if i])
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

@app.route('/details/<int:id>')
def details(id):
    org = OrganizationModel.get_by_id(int(id))
    return render_template("details.html", org = org, posts = json.loads(json.dumps([org], cls=GaeEncoder)), categories=categories, categories_callable=categories_callable)

@app.route('/')
def index():
    all_tags = get_all_tags()
    return render_template("index.html", all_tags=','.join(all_tags))

@app.route('/categories')
def show_categories_all():
    return render_template("categories.html", categories=categories, categories_callable=categories_callable)


@app.route('/search_result', methods = ['GET', 'POST'])
def search_result():
    if request.method == 'GET':
        keyword = request.args.get('category_rus')
    elif request.method == 'POST':
        keyword = request.form.get('search')
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == keyword.lower().strip()).fetch()
    return render_template("search_result.html", posts = json.loads(json.dumps(selected_orgs, cls=GaeEncoder)),
                           categories=categories, categories_callable=categories_callable, keyword=keyword)

# @app.route('/category/<category_eng>')
# def category(category_eng):
#     orgs = OrganizationModel.query(OrganizationModel.category == categories_all[category_eng]).order(-OrganizationModel.when_added).fetch()
#     return render_template("category_with_map.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)),
#                            category_rus=categories_all[category_eng], category_eng=category_eng, categories=categories,
#                            categories_callable=categories_callable)


@app.route('/orgs/new', methods = ['GET', 'POST'])
def new_org():
    category = request.args.get("category_value")
    orgs = OrganizationModel.query(OrganizationModel.category == category).fetch()
    form = OrganizationForm()
    if request.method == 'GET':
        all_tags = get_all_tags()
        return render_template('new_org.html', form=form, categories=categories, categories_callable=categories_callable, posts = json.loads(json.dumps(orgs, cls=GaeEncoder)), all_tags=','.join(all_tags))
    elif request.method == 'POST':
        if form.validate_on_submit():
            tags = form.tags.data.lower().split(',')
            if tags:
                tags.append(form.category.data.lower())
            else:
                tags = [category.lower()]
            if form.title.data != u'Без названия':
                tags.append(form.title.data.lower())
            tags = [t.strip() for t in tags if t]
            tags = list(set(tags))
            post = OrganizationModel(title = form.title.data,
                                    category = form.category.data,
                                    phonenumber = form.phonenumber.data.split(','),
                                    phonenumber_static = form.phonenumber_static.data.split(','),
                                    rating = form.rating.data,
                                    owner = form.owner.data,
                                    adres = form.adres.data,
                                    author = users.get_current_user(),
                                    location = ndb.GeoPt(form.lat.data, form.lng.data),
                                    description = form.description.data,
                                    price = form.price.data,
                                     size = form.size.data,
                                    tags = tags
                                     )
            post.put()
            flash(u'Организация успешно добавлена!')
            add_tags_to_overall(tags)
            category_eng = ''
            for eng, rus in categories_all.iteritems():
                if rus == form.category.data:
                    category_eng = eng
            if category_eng:
                return redirect(url_for('category', category_eng=category_eng))
            else:
                return redirect(url_for('show_categories_all'))
        else:
            flash(u'Форма не прошла валидацию.', 'error')
            all_tags = get_all_tags()
            return render_template('new_org.html', form=form, categories=categories, categories_callable=categories_callable, posts = json.loads(json.dumps(orgs, cls=GaeEncoder)), all_tags=','.join(all_tags))


@app.route('/edit_org/<int:id>', methods = ['GET', 'POST'])
def edit_org(id):
    org = OrganizationModel.get_by_id(int(id))
    if users.is_current_user_admin() or users.get_current_user() == org.author:
        form = OrganizationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                tags = form.tags.data.lower().split(',')
                if tags:
                    tags.append(form.category.data.lower())
                else:
                    tags = [form.category.data.lower()]
                if form.title.data != u'Без названия':
                    tags.append(form.title.data.lower())
                tags = [t.strip() for t in tags if t]
                tags = list(set(tags))
                org.populate(title = form.title.data,
                            category = form.category.data,
                            phonenumber = form.phonenumber.data.split(', '),
                            phonenumber_static = form.phonenumber_static.data.split(', '),
                            rating = form.rating.data,
                            owner = form.owner.data,
                            adres = form.adres.data,
                            location = ndb.GeoPt(form.lat.data, form.lng.data),
                            when_modified = datetime.now(),
                            description = form.description.data,
                             size = form.size.data,
                            tags = tags
                             )
                org.put()
                flash(u'Изменения приняты!')
                add_tags_to_overall(tags)
                category_eng = ''
                for eng, rus in categories_all.iteritems():
                    if rus == form.category.data:
                        category_eng = eng
                if category_eng:
                    return redirect(url_for('category', category_eng=category_eng))
                else:
                    return redirect(url_for('show_categories_all'))
        form.category.data = org.category
        form.title.data = org.title
        form.phonenumber.data = ", ".join(org.phonenumber)
        form.phonenumber_static.data = ", ".join(org.phonenumber_static)
        form.rating.data = org.rating
        form.owner.data = org.owner
        form.adres.data = org.adres
        form.size.data = org.size
        form.description.data = org.description
        if org.location:
            form.lat.data = org.location.lat
            form.lng.data = org.location.lon
        form.tags.data = ",".join(org.tags)
        orgs = OrganizationModel.query(OrganizationModel.category == org.category).fetch()
        all_tags = get_all_tags()
        return render_template("edit_org.html", categories=categories, categories_callable=categories_callable, form=form, id=id, posts = json.loads(json.dumps(orgs, cls=GaeEncoder)), tags=",".join(org.tags), all_tags=','.join(all_tags))
    else:
        flash(u"У вас нет права на редактирование. Вы не являетесь автором этого объекта!", 'error')
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
        flash(u"У вас нет права на удаление. Вы не являетесь автором этого объекта!", 'error')
        return redirect(url_for('category', category_eng=category_eng))

@app.route('/orgs')
def list_orgs():
    orgs = OrganizationModel.query().order(-OrganizationModel.when_added)
    return render_template('list_orgs.html', posts=orgs, categories=categories, categories_callable=categories_callable)

def add_tags_to_overall(tag_list):
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
    return render_template("contacts.html", categories=categories, categories_callable=categories_callable)

@app.route('/traffic')
def traffic():
    return render_template("traffic.html", categories=categories, categories_callable=categories_callable)


######## POST ###########
class PostForm(Form):
    content = TextAreaField('Content', validators=[DataRequired(message=u'Обязятельное поле')])

@app.route('/posts')
def list_posts():
    posts = PostModel.query().order(-PostModel.when)
    return render_template('list_posts.html', posts=posts, categories=categories, categories_callable=categories_callable)

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
    return render_template('new_post.html', form=form, categories=categories, categories_callable=categories_callable)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    post = PostModel(
            content =  request.form['comment'],
            category = request.form['category'],
            organization_id = int(request.form['organization_id']),
            author = users.get_current_user())
    post.put()
    return json.dumps({'status':'OK','comment':request.form['comment']})

@app.route('/get_comments_by_org')
def get_comments_by_org():
    comments_org = PostModel.query(PostModel.organization_id == int(request.args.get('organization_id'))).order(-PostModel.when).fetch()
    return json.dumps({'status':'OK','comments':comments_org}, cls=GaeEncoder)

class SecretForm(Form):
    phonenumber = StringField(widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"(999) 999-9999"})
    phonenumber_static = StringField(widget=widgets.Input(input_type="tel"),render_kw={"placeholder": u"9-99-99"})

@app.route('/secret_query', methods=['GET','POST'])
def secret_query():
    if users.is_current_user_admin():
        formS = SecretForm()
        if request.method == 'POST':
            if formS.validate_on_submit():
                phonenumber = formS.phonenumber.data
                phonenumber_static = formS.phonenumber_static.data
                if request.form['btn'] == u'Мобильный':
                    selected_orgs = OrganizationModel.query(OrganizationModel.phonenumber == phonenumber).fetch()
                else:
                    selected_orgs = OrganizationModel.query(OrganizationModel.phonenumber_static == phonenumber_static).fetch()
                if selected_orgs:
                    return render_template("search_result.html", posts = json.loads(json.dumps(selected_orgs, cls=GaeEncoder)),
                               categories=categories, categories_callable=categories_callable)
                else:
                    all_tags = get_all_tags()
                    form = OrganizationForm()
                    form.phonenumber.data = phonenumber
                    return render_template('new_org.html', form=form, categories=categories, categories_callable=categories_callable,
                                           posts = json.loads(json.dumps({}, cls=GaeEncoder)), all_tags=','.join(all_tags))
        return render_template('secret_query.html', form=formS)
    else:
        flash(u"У вас нет права доступа!", 'error')
        return redirect(url_for('index'))

class AllTagsForm(Form):
    tags = StringField()
    uid = StringField()

@app.route('/secret_allTags', methods=['GET','POST'])
def secret_allTags():
    if users.is_current_user_admin():
        form = AllTagsForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                tags = form.tags.data.lower().split(',')
                all_tags = TagsModel.query(TagsModel.uid == 'myid').get()
                all_tags.all_tags = tags
                all_tags.put()
                flash(u"Изменения приняты!")
                return render_template("secret_allTags.html", form=form)
        all_tags = TagsModel.query(TagsModel.uid == 'myid').get()
        form.tags.data = ",".join(all_tags.all_tags)
        return render_template('secret_allTags.html', form=form)
    else:
        flash(u"У вас нет права доступа!", 'error')
        return redirect(url_for('index'))

def get_nearby_objects(lat,lon):
    area = .0005
    # lat = float(self.request.get('lat'))
    # lon = float(self.request.get('lon'))
    minLat = lat - area
    minLon = lon - area
    maxLat = lat + area
    maxLon = lon + area
    query = ndb.gql("SELECT * FROM OrganizationModel WHERE location >= :1 AND location <=:2",
                         ndb.GeoPt(lat=minLat, lon=minLon), ndb.GeoPt(lat=maxLat, lon=maxLon)).fetch()
    return query