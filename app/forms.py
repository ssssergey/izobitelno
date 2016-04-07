# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, TextAreaField, IntegerField, BooleanField, widgets
from wtforms.fields.html5 import TelField, URLField
from wtforms.validators import DataRequired, NumberRange


class OrganizationForm(Form):
    category = StringField(u'Категория', default=u"")
    title = StringField(u'Название учреждения',default=u"Без названия")
    adres = StringField(u'Адрес', default=u"")
    adres_details = StringField(u'Уточнение к адресу (этаж, рядом с чем и т.д.)', default=u"")
    phonenumber = TelField(u'Мобильные номера',render_kw={"placeholder": u"(999) 999-9999"})
    # phonenumber = StringField(widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"(999) 999-9999"})
    phonenumber_static = StringField(u'Стационарные номера',widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"9-99-99"})
    owner = StringField(u'Контактное лицо', render_kw={"placeholder": u"Иван Иванович"})
    lat = FloatField(default=0)
    lng = FloatField(default=0)
    description = TextAreaField(u'Описание')
    tags = StringField(u'Тэги')
    delivery_terms = StringField(u'Условия доставки')
    working_hours = StringField(u'Режим работы')
    internet_site = URLField(u'Сайт')
    password = StringField(u'Пароль')
    rating = IntegerField(u'Рейтинг', widget=widgets.Input(input_type="tel"), default=0)
    price = IntegerField(u'Цена',widget=widgets.Input(input_type="tel"), default=0)
    size = IntegerField(u'Размер объекта(1-5)', widget=widgets.Input(input_type="tel"), default=2,
                        validators=[NumberRange(message=u'От 1 до 5', min=1, max=5)])
    high_quality = BooleanField(u'Высокое качество', default=False)
    delivery = BooleanField(u'Доставка',default=False)
    daynight = BooleanField(u'Круглосуточно',default=False)
    new = BooleanField(u'Мы открылись',default=False)


class CommentForm(Form):
    content = TextAreaField('Content', validators=[DataRequired(message=u'Обязятельное поле')])


class DeleteTagForm(Form):
    tag = StringField(default=u"")


class ReplaceTagForm(Form):
    tag_del = StringField(validators=[DataRequired(message=u'Обязятельное поле')])
    tag_add = StringField(validators=[DataRequired(message=u'Обязятельное поле')])


class GetAllTagsForm(Form):
    tags = StringField()


class SecretPhoneForm(Form):
    phonenumber = StringField(widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"(999) 999-9999"})
    phonenumber_static = StringField(widget=widgets.Input(input_type="tel"), render_kw={"placeholder": u"9-99-99"})
