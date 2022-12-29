from flask import flash, redirect, url_for, render_template, request, jsonify
from flask_login import login_required, login_user, logout_user
from sqlalchemy.sql.functions import user

from . import gj_test_bp as gj_test

from .models import *
from .forms import TestListForm, LoginForm, RegisterForm, SpecimenForm
from .. import csrf


@gj_test.route('/landing')
def landing():
    return render_template('gj_test/landing.html')


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
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email, password=password).first()
        if user and user.verify_password(password):
            login_user(user)
            flash('Logged in successfully')
        else:
            flash('Logged in unsuccessfully')
        return redirect(url_for('gj_test.landing'))
    return render_template('gj_test/login.html', form=form)


@gj_test.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('gj_test.landing'))


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


@gj_test.route('/tests/view')
def view_tests():
    return render_template('gj_test/view_tests.html')


@gj_test.route('/api/view-tests')
def get_tests_view_data():
    query = GJTest.query
    search = request.args.get('search[value]')
    query = query.filter(db.or_(
        GJTest.test_name.like(u'%{}%'.format(search)),
        GJTest.code.like(u'%{}%'.format(search)),

    ))
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for test in query:
        test_data = test.to_dict()
        # test_data['view'] = '<a href="{}"><i class="fas fa-eye"></i></a>'.format(
        #     url_for())
        # test_data['edit'] = '<a href="{}"><i class="fas fa-edit"></i></a>'.format(
        #     url_for())
        data.append(test_data)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': GJTest.query.count(),
                    'draw': request.args.get('draw', type=int),
                    })


@gj_test.route('/specimen/add', methods=['GET', 'POST'])
def add_specimen_ref():
    specimen = db.session.query(GJTestSpecimen)
    form = SpecimenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_specimen = GJTestSpecimen()
            form.populate_obj(new_specimen)
            db.session.add(new_specimen)
            db.session.commit()
            flash('New specimen has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/specimen_ref.html', form=form, specimen=specimen, url_callback=request.referrer)
