from flask import flash, redirect, url_for, render_template, request, jsonify
from flask_login import login_required, login_user, logout_user
from sqlalchemy.sql.functions import user

from . import gj_test_bp as gj_test

from .models import *
from .forms import TestListForm, LoginForm, RegisterForm, SpecimenForm, LocationForm, TimePeriodRequestedForm, \
    WaitingTimeForm, TestDateForm, SpecimenTransportationForm
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
        return redirect(url_for('gj_test.view_tests'))
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
    return redirect(url_for('gj_test.login'))


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
        test_data['view'] = '<a href="{}" class="button is-small is-primary is-outlined">ดูข้อมูลเพิ่ม</a>'.format(
            url_for('gj_test.view_info_test', test_id=test.id ))
        test_data['edit'] = '<a href="{}" class="button is-small is-danger is-outlined">แก้ไขข้อมูล </a>'.format(
            url_for('gj_test.edit_test', test_id=test.id))
        data.append(test_data)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': GJTest.query.count(),
                    'draw': request.args.get('draw', type=int),
                    })


@gj_test.route('/specimen/add', methods=['GET', 'POST'])
def add_specimen_ref():
    form = SpecimenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_specimen = GJTestSpecimen()
            form.populate_obj(new_specimen)
            db.session.add(new_specimen)
            db.session.commit()
            flash('New specimen has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/specimen_ref.html', form=form, url_callback=request.referrer)


@gj_test.route('/location/add', methods=['GET', 'POST'])
def add_location_ref():
    form = LocationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_location = GJTestLocation()
            form.populate_obj(new_location)
            db.session.add(new_location)
            db.session.commit()
            flash('New location has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/location_ref.html', form=form, url_callback=request.referrer)


@gj_test.route('/time-period-requested/add', methods=['GET', 'POST'])
def add_time_period_requested_ref():
    form = TimePeriodRequestedForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_time_period_requested = GJTestTimePeriodRequest()
            form.populate_obj(new_time_period_requested)
            db.session.add(new_time_period_requested)
            db.session.commit()
            flash('New time period request has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/time_period_requested_ref.html', form=form, url_callback=request.referrer)


@gj_test.route('/new-waiting/add', methods=['GET', 'POST'])
def add_new_waiting_ref():
    form = WaitingTimeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_waiting_time = GJTestWaitingPeriod()
            form.populate_obj(new_waiting_time)
            db.session.add(new_waiting_time)
            db.session.commit()
            flash('New waiting has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/new_waiting_ref.html', form=form, url_callback=request.referrer)


@gj_test.route('/test-date/add', methods=['GET', 'POST'])
def add_test_date_ref():
    form = TestDateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_test_date = GJTestDate()
            form.populate_obj(new_test_date)
            db.session.add(new_test_date)
            db.session.commit()
            flash('New test date has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/new_test_date_ref.html', form=form, url_callback=request.referrer)


@gj_test.route('/specimen-transportation/add', methods=['GET', 'POST'])
def add_specimen_transportation_ref():
    form = SpecimenTransportationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_specimen_transportation = GJTestSpecimenTransportation()
            form.populate_obj(new_specimen_transportation)
            db.session.add(new_specimen_transportation)
            db.session.commit()
            flash('New specimen transportation has been added.', 'success')
            return redirect(url_for('gj_test.add_test', form=form))
    return render_template('gj_test/specimen_transportation.html', form=form, url_callback=request.referrer)


@gj_test.route('/info-tests/view/<int:test_id>')
def view_info_test(test_id):
    test = GJTest.query.get(test_id)
    return render_template('gj_test/view_info_test.html',
                           test=test)


@gj_test.route('/edit/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    test = GJTest.query.get(test_id)
    form = TestListForm(obj=test)
    if request.method == 'POST':
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash(u'แก้ไขข้อมูลเรียบร้อย', 'success')
        return redirect(url_for('gj_test.view_info_tests', test_id=test.id))
    return render_template('gj_test/edit_test.html', form=form, test=test)