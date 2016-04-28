# -*- coding: utf-8 -*-
import json
import urllib2
from datetime import datetime
# from passlib.handlers.sha2_crypt import sha256_crypt

from google.appengine.api import users, datastore_types
from google.appengine.ext import ndb
from google.appengine.api import memcache

from flask import render_template, redirect, flash, url_for, request, g, abort, session
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, lm
from models import CommentModel, OrganizationModel, TagsModel, SearchWordsModel, UserModel
from forms import OrganizationForm, CommentForm, DeleteTagForm, ReplaceTagForm, GetAllTagsForm, SecretPhoneForm, \
    RegistrationForm, LoginForm

from app.data import categories

from token import generate_confirmation_token, confirm_token
from email import send_email


class GaeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return (obj - datetime(1970, 1, 1)).total_seconds()
        # elif isinstance(obj, list):
        #     return ', '.join([i for i in obj if i])
        elif isinstance(obj, ndb.Model):
            result = obj.to_dict()
            result['id'] = obj.key.id()
            return result
        elif isinstance(obj, users.User):
            return obj.nickname()
        elif isinstance(obj, UserModel):
            return obj.nickname
        elif isinstance(obj, datastore_types.GeoPt):
            return {'lat': obj.lat, 'lng': obj.lon}
        else:
            return json.JSONEncoder.default(self, obj)


###################Login->


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(id):
    return UserModel.get_by_id(int(id))


@lm.unauthorized_handler
def unauthorized():
    return redirect(url_for('login', url_back=request.url))
    return render_template('401.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = UserModel.query(UserModel.email == form.email.data.strip()).get()
        if user and user.password == form.password.data:
            login_user(user, remember=True)
            flash(u'Вы успешно вошли по паролю!')
            return redirect(session['url_back'] or url_for('index'))
    session['url_back'] = request.args.get('url_back')
    return render_template('auth/login.html', form=form)


@app.route('/login_google', methods=['GET', 'POST'])
def login_google():
    google_user = users.get_current_user()
    if google_user:
        flask_user = UserModel.query(UserModel.google_user == google_user).get()
        if not flask_user:
            flask_user = UserModel(google_user=google_user, nickname=google_user.nickname(), email=google_user.email(),
                                   email_confirmed=True, email_confirmed_on=datetime.now())
            flask_user.put()
        if users.is_current_user_admin():
            flask_user.is_admin = True
            flask_user.put()
        login_user(flask_user, remember=True)
        flash(u'Вы успешно залогинились по аккунту Google!')
        return redirect(session['url_back'] or url_for('index'))
    return redirect(users.create_login_url(request.url))


@app.route('/login_vk', methods=['GET', 'POST'])
def login_vk():
    vk_app_id = "5437643"
    vk_client_secret = "BZMjgoDhd8lW4iIVw5hC"
    if request.args.get('bussiness'):
        vk_scope = "email,photos,audio,video,docs,notes,pages,status,wall,notifications,stats,ads,market,offline,nohttps"
    else:
        vk_scope = "email"
    login_attempt = request.args.get('login_attempt')

    code = request.args.get('code')
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    if login_attempt:
        return redirect("https://oauth.vk.com/authorize?client_id={}&display=page&redirect_uri={}&scope={}"
                        "&response_type=code&v=5.52".format(vk_app_id, url_for('login_vk', _external=True), vk_scope))
    if code:
        print code
        url_get_token = "https://oauth.vk.com/access_token?client_id={}&client_secret={}&redirect_uri={}" \
                        "&code={}".format(vk_app_id, vk_client_secret, url_for('login_vk', _external=True), code)
        req = urllib2.Request(url_get_token)
        opener = urllib2.build_opener()
        f = opener.open(req)
        json_obj = json.loads(f.read())
        print json_obj
        access_token = json_obj.get('access_token')
        expires_in = json_obj.get('expires_in')
        user_id = json_obj.get('user_id')
        email = json_obj.get('email')
        if user_id and access_token:
            url_getProfiles = "https://api.vkontakte.ru/method/getProfiles?uid={}&access_token={}".format(user_id,
                                                                                                          access_token)
            # {"response":[{"uid":10758791,"first_name":"Вася","last_name":"Пупкин"}]}
            req = urllib2.Request(url_getProfiles)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json_obj = json.loads(f.read())
            nickname = u"{} {}".format(json_obj['response'][0]['first_name'], json_obj['response'][0]['last_name'])
            flask_user = UserModel.query(UserModel.vk_user_id == user_id).get()
            if not flask_user:
                flask_user = UserModel(
                    nickname=nickname,
                    vk_user_id=user_id,
                    vk_access_token=access_token,
                    vk_expires_in=expires_in,
                )
                if email:
                    flask_user.email = email
                    flask_user.email_confirmed = True
                    flask_user.email_confirmed_on = datetime.now()
                flask_user.put()
            login_user(flask_user, remember=True)
            flash(u'Вы успешно залогинились по аккунту ВКонтакте!')
            return redirect(session['url_back'] or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    flash(u'Вы вышли из своего аккаунта')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        user = UserModel.query(UserModel.email == form.email.data.strip()).get()
        if user:
            flash(u'Такой email уже зарегистрирован! Если Вы забыли пароль, свяжитесь с администратором.', 'danger')
            return render_template('auth/register.html', form=form)
        user = UserModel(
            nickname=form.email.data,
            email=form.email.data,
            password=form.password.data,
            email_confirmed=False
        )
        user.put()

        # token = generate_confirmation_token(comments.email)
        # confirm_url = url_for('confirm_email', token=token, _external=True)
        # html = render_template('auth/activate.html', confirm_url=confirm_url)
        # subject = u"Подтвердите свой email"
        # send_email(comments.email, subject, html)

        login_user(user)
        flash(u'Вы зарегистрировались. Не теряйте пароль.', 'success')
        # flash(u'Письмо для подтверждения регистрации было отправлено на указанный адрес. Откройте письмо и подтвердите '
        #       u'регистрацию.', 'success')
        return redirect(session['url_back'] or url_for('index'))

    session['url_back'] = request.args.get('url_back')
    return render_template('auth/register.html', form=form)


@app.route('/confirm/<token>')
# @login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash(u'Вы просрочили подтверждение почты или ссылка оказалась неверной.', 'danger')
        return redirect(url_for('index'))
    user = UserModel.query(UserModel.email == email).get()
    if user.confirmed:
        flash(u'Аккаунт уже подтвержден.Войдите под своими почтой и паролем.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        user.put()
        flash(u'Вы подтвердили свой аккаунт. Спасибо!', 'success')
    return redirect(url_for('index'))


#################<-Login


@app.route('/')
def index():
    all_tags = get_all_tags()
    return render_template("index.html", all_tags=','.join(all_tags))


@app.route('/details/<int:id>')
def details(id):
    org = OrganizationModel.get_by_id(int(id))
    return render_template("details.html", org=org, posts=json.loads(json.dumps([org], cls=GaeEncoder)),
                           categories=categories)


@app.route('/categories')
def show_categories_all():
    return render_template("categories.html", categories=categories)


@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    if request.method == 'GET':
        keyword = request.args.get('category_rus')
    elif request.method == 'POST':
        keyword = request.form.get('search')
        word = SearchWordsModel.query(SearchWordsModel.word == keyword.lower().strip()).get()
        if word:
            word.quantity = word.quantity + 1
            word.put()
        else:
            word = SearchWordsModel(word=keyword.lower().strip(), quantity=1)
            word.put()
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == keyword.lower().strip()).fetch()
    return render_template("search_result.html", posts=json.loads(json.dumps(selected_orgs, cls=GaeEncoder)),
                           categories=categories, keyword=keyword)


# @app.route('/category/<category_eng>')
# def category(category_eng):
#     orgs = OrganizationModel.query(OrganizationModel.category == categories_all[category_eng]).order(-OrganizationModel.when_added).fetch()
#     return render_template("category_with_map.html", posts = json.loads(json.dumps(orgs, cls=GaeEncoder)),
#                            category_rus=categories_all[category_eng], category_eng=category_eng, categories=categories,
#                            categories_callable=categories_callable)


@app.route('/orgs/new', methods=['GET', 'POST'])
@login_required
def new_org():
    # category = request.args.get("category_value") # Delete
    orgs = OrganizationModel.query().fetch()
    form = OrganizationForm(request.form)
    if request.method == 'GET':
        all_tags = get_all_tags()
        if request.args.get('keyword'):
            form.tags.data = request.args.get('keyword')
        else:
            form.tags.data = ''
        return render_template('new_org.html', form=form, categories=categories,
                               posts=json.loads(json.dumps(orgs, cls=GaeEncoder)), all_tags=','.join(all_tags))
    elif request.method == 'POST':
        if form.validate_on_submit():
            tags = form.tags.data.lower().split(',')
            # if tags:
            #     tags.append(form.category.data.lower()) # Delete
            # else:
            #     tags = [category.lower()]
            if form.title.data != u'Без названия':
                tags.append(form.title.data.lower())
            tags = [t.strip() for t in tags if t]
            tags = list(set(tags))
            add_tags_to_overall(tags)
            post = OrganizationModel(title=form.title.data,
                                     tags=tags,
                                     category=form.category.data,
                                     phonenumber=form.phonenumber.data.split(','),
                                     phonenumber_static=form.phonenumber_static.data.split(','),
                                     rating=form.rating.data,
                                     owner=form.owner.data,
                                     adres=form.adres.data,
                                     adres_details=form.adres_details.data,
                                     author=current_user.nickname,
                                     location=ndb.GeoPt(form.lat.data, form.lng.data),
                                     description=form.description.data,
                                     price=form.price.data,
                                     size=form.size.data,
                                     delivery=form.delivery.data,
                                     delivery_terms=form.delivery_terms.data,
                                     working_hours=form.working_hours.data,
                                     daynight=form.daynight.data,
                                     high_quality=form.high_quality.data,
                                     internet_site=form.internet_site.data,
                                     )
            post.put()
            flash(u'Организация успешно добавлена!')
            return redirect(url_for('show_categories_all'))
        else:
            flash(u'Форма не прошла валидацию.', 'error')
            all_tags = get_all_tags()
            return render_template('new_org.html', form=form, categories=categories,
                                   posts=json.loads(json.dumps(orgs, cls=GaeEncoder)), all_tags=','.join(all_tags))


@app.route('/edit_org/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_org(id):
    org = OrganizationModel.get_by_id(int(id))
    if users.is_current_user_admin():
        form = OrganizationForm(request.form)
        if request.method == 'POST':
            if form.validate_on_submit():
                tags = form.tags.data.lower().split(',')
                # if tags:
                #     tags.append(form.category.data.lower())
                # else:
                #     tags = [form.category.data.lower()]
                if form.title.data != u'Без названия':
                    tags.append(form.title.data.lower())
                tags = [t.strip() for t in tags if t]
                tags = list(set(tags))
                add_tags_to_overall(tags)
                org.populate(title=form.title.data,
                             category=form.category.data,
                             phonenumber=form.phonenumber.data.split(', '),
                             phonenumber_static=form.phonenumber_static.data.split(', '),
                             rating=form.rating.data,
                             owner=form.owner.data,
                             adres=form.adres.data,
                             adres_details=form.adres_details.data,
                             location=ndb.GeoPt(form.lat.data, form.lng.data),
                             when_modified=datetime.now(),
                             description=form.description.data,
                             size=form.size.data,
                             tags=tags,
                             delivery=form.delivery.data,
                             delivery_terms=form.delivery_terms.data,
                             working_hours=form.working_hours.data,
                             daynight=form.daynight.data,
                             high_quality=form.high_quality.data,
                             internet_site=form.internet_site.data,
                             )
                org.put()
                flash(u'Изменения приняты!')
                return redirect(url_for('show_categories_all'))
        form.category.data = org.category
        form.title.data = org.title
        form.phonenumber.data = ", ".join(org.phonenumber)
        form.phonenumber_static.data = ", ".join(org.phonenumber_static)
        form.rating.data = org.rating
        form.owner.data = org.owner
        form.adres.data = org.adres
        form.adres_details.data = org.adres_details
        form.size.data = org.size
        form.description.data = org.description
        if org.location:
            form.lat.data = org.location.lat
            form.lng.data = org.location.lon
        form.tags.data = ",".join(org.tags)
        form.delivery.data = org.delivery
        form.delivery_terms.data = org.delivery_terms
        form.working_hours.data = org.working_hours
        form.internet_site.data = org.internet_site
        form.daynight.data = org.daynight
        form.high_quality.data = org.high_quality
        keyword = request.args.get('keyword')
        if keyword:
            orgs = OrganizationModel.query(OrganizationModel.tags == keyword.lower().strip()).fetch()
        else:
            orgs = [OrganizationModel.get_by_id(int(id))]
        all_tags = get_all_tags()
        return render_template("edit_org.html", categories=categories,
                               form=form, id=id, posts=json.loads(json.dumps(orgs, cls=GaeEncoder)),
                               tags=",".join(org.tags), all_tags=','.join(all_tags), keyword=keyword)
    else:
        flash(u"У вас нет права на редактирование. Вы не являетесь автором этого объекта!", 'error')
        return redirect(url_for('index'))


@app.route('/del_org/<int:id>', methods=['GET', 'DELETE'])
@login_required
def del_org(id):
    org = OrganizationModel.get_by_id(int(id))
    if users.is_current_user_admin():
        flash(u"Вы успешно удалили объект как администратор!")
        org.key.delete()
        return redirect(url_for('index'))
    if current_user.nickname == org.author:
        flash(u"Вы успешно удалили объект как автор!")
        org.key.delete()
        return redirect(url_for('index'))
    else:
        flash(u"У вас нет права на удаление. Вы не являетесь автором этого объекта!", 'error')
        return redirect(url_for('index'))


@app.route('/orgs')
def list_orgs():
    orgs = OrganizationModel.query().order(-OrganizationModel.when_added)
    return render_template('admin/list_orgs.html', posts=orgs, categories=categories)


### Edit all_Tags
def add_tags_to_overall(tag_list):
    new_list = []
    tags_from_ds = TagsModel.query(TagsModel.uid == 'myid').get()
    # Если нет такой записи,то создаем ее
    if not tags_from_ds:
        tags_from_ds = TagsModel(uid='myid')
    old_list = tags_from_ds.all_tags
    new_list = list(set(old_list + tag_list))
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


def get_nearby_objects(lat, lon):
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


######## COMMENTS ###########

@app.route('/comments/get_all')
def get_all_comments():
    posts = CommentModel.query().order(-CommentModel.when)
    for post in posts:
        if post.organization_id:
            org = OrganizationModel.get_by_id(int(post.organization_id))
            if org:
                org_name = org.title
            else:
                org_name = u'Неизвестно'
        else:
            org_name = u'Неизвестно'
        post.org = org_name
    return render_template('comments/get_all_comments.html', posts=posts, categories=categories)


@app.route('/comment_new/general', methods=['GET', 'POST'])
def comment_new_general():
    form = CommentForm()
    if not current_user.is_authenticated:
        author = u'Аноним'
    else:
        author = current_user.nickname
    if form.validate_on_submit():
        post = CommentModel(
            content=request.form['content'],
            # category=request.form['category'],
            # organization_id=int(request.form['organization_id']),
            author=author,
        )
        post.put()
        flash(u'Комментарий успешно создан!')
        return redirect(url_for('get_all_comments'))
    return render_template('comments/new_comment.html', form=form, categories=categories)


## For Ajax
@app.route('/comment_new/from_details', methods=['POST'])
def comment_new_details():
    if not current_user.is_authenticated:
        author = u'Аноним'
    else:
        author = current_user.nickname
    post = CommentModel(
        content=request.form['comment'],
        category=request.form['category'],
        organization_id=int(request.form['organization_id']),
        author=author,
    )
    post.put()
    return json.dumps({'status': 'OK', 'comment': request.form['comment']})


@app.route('/comments/get_by_org')
def get_comments_by_org():
    comments_org = CommentModel.query(CommentModel.organization_id == int(request.args.get('organization_id'))).order(
        -CommentModel.when).fetch()
    return json.dumps({'status': 'OK', 'comments': comments_org}, cls=GaeEncoder)


######## COMMENTS_END ###########

@app.route('/like')
# @login_required
def like():
    if current_user.is_authenticated:
        org_id = int(request.args.get('organization_id'))
        user = UserModel.get_by_id(int(current_user.id))
        if org_id in user.liked_orgs:
            user.liked_orgs.remove(org_id)
            user.put()
            org = OrganizationModel.get_by_id(int(org_id))
            org.rating -= 1
            org.put()
            return json.dumps({'status': 'OK', 'rating_minus': str(org.rating)}, cls=GaeEncoder)
        else:
            user.liked_orgs.append(org_id)
            user.put()
            org = OrganizationModel.get_by_id(int(org_id))
            org.rating += 1
            org.put()
            return json.dumps({'status': 'OK', 'rating_plus': str(org.rating)}, cls=GaeEncoder)
    return json.dumps({'status': 'OK', 'notlogin': [u'Чтобы ставить оценку, вам нужно войти.', request.url]},
                      cls=GaeEncoder)


#### ADMIN FUNCTIONS
### Edit tags in entities

@app.route('/admin/secret_edit_tags', methods=['GET', 'POST'])
def secret_edit_tags():
    if users.is_current_user_admin():
        form1 = DeleteTagForm(prefix="form1")
        form2 = ReplaceTagForm(prefix="form2")
        form3 = ReplaceTagForm(prefix="form3")
        if request.method == 'POST':
            if form1.validate_on_submit() and request.form['btn'] == u'Удалить':
                delete_some_tags(form1.tag.data.strip())
                flash(u'Удаление прошло успешно')
                redirect(url_for('secret_edit_tags'))
            elif form2.validate_on_submit() and request.form['btn'] == u'Заменить':
                replace_some_tags(form2.tag_del.data.strip(), form2.tag_add.data.strip())
                flash(u'Замена прошла успешно')
                redirect(url_for('secret_edit_tags'))
            elif form3.validate_on_submit() and request.form['btn'] == u'Дополнить':
                append_some_tags(form3.tag_del.data.strip(), form3.tag_add.data.strip())
                flash(u'Дополнение прошло успешно')
                redirect(url_for('secret_edit_tags'))
                # elif form1.validate_on_submit() and request.form['btn'] == u'Заполнить':
                #     populate_empty_tags()
                #     flash(u'Заполнение прошло успешно')
                #     redirect(url_for('secret_edit_tags'))
        return render_template("admin/secret_edit_tags.html", form1=form1, form2=form2, form3=form3)
    else:
        flash(u"У вас нет права доступа!", 'error')
        return redirect(url_for('index'))


# def populate_empty_tags():
#     selected_orgs = OrganizationModel.query().fetch()
#     updated = []
#     for entity in selected_orgs:
#         if not entity.tags:
#             entity.tags.append(entity.title.lower().strip())
#             if entity.title.lower().strip() != entity.category.lower().strip():
#                 entity.tags.append(entity.category.lower().strip())
#             updated.append(entity)
#             add_tags_to_overall([entity.title.lower().strip()])
#     ndb.put_multi(updated)

def append_some_tags(tag_to_find, tag_to_add):
    # APPEND in orgs
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == tag_to_find.lower().strip()).fetch()
    updated = []
    for entity in selected_orgs:
        if tag_to_add not in entity.tags:
            entity.tags.append(tag_to_add)
            updated.append(entity)
    ndb.put_multi(updated)
    # APPEND in allTags
    all_tags = TagsModel.query(TagsModel.uid == 'myid').fetch()
    if tag_to_add not in all_tags[0].all_tags:
        all_tags[0].all_tags.append(tag_to_add)
        all_tags[0].put()
    get_all_tags(True)


def replace_some_tags(tag_to_delete, tag_to_add):
    # replace in orgs
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == tag_to_delete.lower().strip()).fetch()
    updated = []
    for entity in selected_orgs:
        entity.tags.remove(tag_to_delete)
        entity.tags.append(tag_to_add)
        updated.append(entity)
    ndb.put_multi(updated)
    # replace in allTags
    all_tags = TagsModel.query(TagsModel.uid == 'myid').fetch()
    try:
        all_tags[0].all_tags.remove(tag_to_delete)
        all_tags[0].all_tags.append(tag_to_add)
        all_tags[0].put()
    except:
        pass
    get_all_tags(True)


def delete_some_tags(tag_to_delete):
    # Delete form orgs
    selected_orgs = OrganizationModel.query(OrganizationModel.tags == tag_to_delete.lower().strip()).fetch()
    updated = []
    for entity in selected_orgs:
        entity.tags.remove(tag_to_delete)
        updated.append(entity)
    ndb.put_multi(updated)
    # Delete form allTags
    all_tags = TagsModel.query(TagsModel.uid == 'myid').fetch()
    try:
        all_tags[0].all_tags.remove(tag_to_delete)
        all_tags[0].put()
    except:
        pass
    get_all_tags(True)


### Get all tags list into template to edit

@app.route('/admin/secret_get_allTags', methods=['GET', 'POST'])
def secret_get_allTags():
    if users.is_current_user_admin():
        form = GetAllTagsForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                tags = form.tags.data.lower().split(',')
                all_tags = TagsModel.query(TagsModel.uid == 'myid').get()
                all_tags.all_tags = tags
                all_tags.put()
                flash(u"Изменения приняты!")
                return render_template("admin/secret_get_AllTags.html", form=form)
        all_tags = TagsModel.query(TagsModel.uid == 'myid').get()
        if all_tags:
            form.tags.data = ",".join(all_tags.all_tags)
        else:
            form.tags.data = ""
        return render_template('admin/secret_get_AllTags.html', form=form)
    else:
        flash(u"У вас нет права доступа!", 'error')
        return redirect(url_for('index'))


### Find entity by phone, if not go to new_org with this phone


@app.route('/admin/secret_query_by_phonenumber', methods=['GET', 'POST'])
def secret_query_by_phonenumber():
    if users.is_current_user_admin():
        formS = SecretPhoneForm()
        if request.method == 'POST':
            if formS.validate_on_submit():
                phonenumber = formS.phonenumber.data
                phonenumber_static = formS.phonenumber_static.data
                if request.form['btn'] == u'Мобильный':
                    selected_orgs = OrganizationModel.query(OrganizationModel.phonenumber == phonenumber).fetch()
                else:
                    selected_orgs = OrganizationModel.query(
                        OrganizationModel.phonenumber_static == phonenumber_static).fetch()
                if selected_orgs:
                    return render_template("search_result.html",
                                           posts=json.loads(json.dumps(selected_orgs, cls=GaeEncoder)),
                                           categories=categories)
                else:
                    all_tags = get_all_tags()
                    form = OrganizationForm()
                    form.phonenumber.data = phonenumber
                    return render_template('new_org.html', form=form, categories=categories,
                                           posts=json.loads(json.dumps({}, cls=GaeEncoder)),
                                           all_tags=','.join(all_tags))
        return render_template('admin/secret_query_by_phonenumber.html', form=formS)
    else:
        flash(u"У вас нет права доступа!", 'error')
        return redirect(url_for('index'))
