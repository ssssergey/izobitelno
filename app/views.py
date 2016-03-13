from flask import render_template, redirect, flash, url_for
from app import app
from models import Post
from decorators import login_required
from google.appengine.api import users

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired,Length,EqualTo

class PostForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

@app.route('/posts')
def list_posts():
    posts = Post.all()
    return render_template('list_posts.html', posts=posts)

@app.route('/posts/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,
                    content = form.content.data,
                    author = users.get_current_user())
        post.put()
        flash('Post saved on database.')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html', form=form)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/traffic')
def traffic():
    return render_template("traffic.html")

@app.route('/location')
def location():
    return render_template("location.html")
