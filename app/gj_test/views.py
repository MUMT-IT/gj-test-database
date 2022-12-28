from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, login_user, logout_user
from sqlalchemy.sql.functions import user

from . import gj_test_bp as gj_test

from .models import *
from .forms import TestListForm, LoginForm, RegisterForm
from .. import csrf


@gj_test.route('/')
def index():
    return 'Hello, world'


@csrf.exempt
@gj_test.route('/new-test/add', methods=['GET', 'POST'])
def add_test():
    form = TestListForm()

    if form.validate_on_submit():
        test = GJTest()
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
        # return redirect(url_for('gj_test.view_test'))
        # Check Error
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('gj_test/new_test.html', form=form)


@csrf.exempt
@gj_test.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            redirect_url = request.args.get('next') or url_for('gj_test.login')
            return redirect(redirect_url)
    return render_template('gj_test/login.html', form=form)


@gj_test.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('gj_test.index'))


@csrf.exempt
@gj_test.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        new_user = User(
            username=username,
            email=email,
            password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully')
        return redirect(url_for('gj_test.login'))
    return render_template('gj_test/register.html', form=form, errors=form.errors)
