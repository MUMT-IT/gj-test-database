import os

from flask import flash, redirect, url_for, render_template, request, jsonify, abort, send_from_directory
from flask_admin.helpers import is_safe_url
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from itsdangerous import TimedJSONWebSignatureSerializer
from pandas import read_excel, isna, DataFrame
from sqlalchemy.sql.functions import user
from werkzeug.utils import secure_filename

from app import app, mail

from . import gj_test_bp as gj_test

from .models import *
from .forms import TestListForm, LoginForm, RegisterForm, SpecimenForm, LocationForm, TimePeriodRequestedForm, \
    WaitingTimeForm, TestDateForm, SpecimenTransportationForm, ForgotPasswordForm, ResetPasswordForm
from .. import csrf

ALLOWED_EXTENSIONS = ['xlsx', 'xls']


def send_mail(recp, title, message):
    message = Message(subject=title, body=message, recipients=recp)
    mail.send(message)


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
    return render_template('gj_test/new_test.html', form=form, url_callback=url_for('gj_test.view_tests'))


@csrf.exempt
@gj_test.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        if next:
            return redirect(next)
        else:
            return redirect(url_for('gj_test.landing'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            password = form.password.data
            if user.verify_password(password):
                login_user(user, form.remember_me.data)
                flash(u'Logged in successfully ลงทะเบียนสำเร็จ', 'success')
                return redirect(url_for('gj_test.landing'))
            else:
                flash(u'Wrong password, try again. รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง', 'danger')
                return redirect(url_for('gj_test.login'))
        else:
            flash(u'User does not exists. ไม่พบบัญชีผู้ใช้ในระบบ', 'danger')
            return redirect(url_for('gj_test.register'))

    return render_template('gj_test/login.html', form=form, errors=form.errors)


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
        flash(u'Registered system successfully สมัครระบบสำเร็จ', 'success')
        return redirect(url_for('gj_test.login'))
    return render_template('gj_test/register.html', form=form, errors=form.errors)


@gj_test.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    email = request.args.get('email')
    serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'))
    try:
        token_data = serializer.loads(token)
    except Exception as e:
        print(str(e))
        return u'Bad JSON Web token. You need a valid token to reset the password.' \
               u'รหัสสำหรับทำการตั้งค่า password หมดอายุหรือไม่ถูกต้อง'
    if token_data.get('email') != email:
        return u'Invalid JSON Web token.'

    user = User.query.filter_by(email=email).first()
    if not user:
        flash(u'User does not exists. ไม่พบชื่อบัญชีในฐานข้อมูล')
        return redirect(url_for('gj_test.register'))

    form = ResetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user.password = form.new_pass.data
            db.session.add(user)
            db.session.commit()
            flash(u'Password has been reset. ตั้งค่ารหัสผ่านใหม่เรียบร้อย', 'success')
            return redirect(url_for('gj_test.login'))
    return render_template('gj_test/reset_password.html', form=form, errors=form.errors)


@gj_test.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect('gj_test.landing')
    form = ForgotPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if not user:
                flash(u'User not found. ไม่พบบัญชีในฐานข้อมูล', 'warning')
                return render_template('gj_test/forgot_password.html', form=form, errors=form.errors)
            serializer = TimedJSONWebSignatureSerializer(app.config.get('SECRET_KEY'), expires_in=72000)
            token = serializer.dumps({'email': form.email.data})
            url = url_for('gj_test.reset_password', token=token, email=form.email.data, _external=True)
            message = u'Click the link below to reset the password.' \
                      u' กรุณาคลิกที่ลิงค์เพื่อทำการตั้งค่ารหัสผ่านใหม่\n\n{}'.format(url)
            print(form.email.data)
            try:
                send_mail(['{}'.format(form.email.data)],
                          title='MUMT-GJ: Password Reset. ตั้งรหัสผ่านใหม่สำหรับระบบ MUMT-GJ',
                          message=message)
            except Exception as e:
                print(str(e))
                flash(u'Failed to send an email to {}. ระบบไม่สามารถส่งอีเมลได้กรุณาตรวจสอบอีกครั้ง' \
                      .format(form.email.data), 'danger')
            else:
                flash(u'Please check your email for the link to reset the password within 20 minutes.'
                      u' โปรดตรวจสอบอีเมลของท่านเพื่อทำการแก้ไขรหัสผ่านภายใน 20 นาที', 'success')
            return redirect(url_for('gj_test.login'))
    return render_template('gj_test/forgot_password.html', form=form, errors=form.errors)


@gj_test.route('/tests/view')
def view_tests():
    return render_template('gj_test/view_tests.html', url_callback=request.referrer)


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
        test_data['view'] = '<a href="{}" class="button is-small is-primary is-outlined">ดูข้อมูล</a>'.format(
            url_for('gj_test.view_info_test', test_id=test.id))
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
        return redirect(url_for('gj_test.view_tests'))
    return render_template('gj_test/edit_test.html', form=form, test=test, url_callback=request.referrer)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@gj_test.route('tests/template/download', methods=['GET'])
def download_test_template():
    records = []

    records.append({
        u'การทดสอบ': u'ABO Group',
        u'รหัส': u'MT0304900',
        u'ข้อบ่งชี้ในการส่งตรวจ': u'ตรวจหาหมู่เลือด ABO',
        u'การเตรียมผู้ป่วย': u'-',
        u'ชนิด': u'EDTA Blood',
        u'ปริมาณ': u'3',
        u'หน่วย': u'ml',
        u'ภาชนะ': u'หลอดเลือดสูญญากาศจุกสีม่วง',
        u'วัน/วันเวลา': u'ทุกวันตลอด 24 ชั่วโมง',
        u'สถานที่': u'ห้องปฏิบัติการศูนย์เทคนิคการแพทย์ฯ',
        u'วิธี/หลักการ': u'Tube technique',
        u'วันที่ทำการทดสอบ': u'ทุกวัน',
        u'ปกติ': u'1 ชั่วโมง',
        u'ด่วน': u'A, B, O, AB',
        u'การรายงานผลและค่าอ้างอิง': u'-',
        u'ระยะเวลาที่สามารถขอตรวจเพิ่มได้': u'ภายใน 24 ชั่วโมง',
        u'สิ่งรบกวนต่อการตรวจวิเคราะห์': u'สิ่งส่งตรวจ Clot',
        u'ข้อควรระวังและอื่นๆ': u'นำส่งภายใน 2 ชั่วโมงหลังเจาะเลือด',
        u'สถานที่ทำการทดสอบ': u'ห้องปฏิบัติการศูนย์เทคนิคการแพทย์ฯ'
    })
    df = DataFrame(records)
    df.to_excel('test_template.xlsx')
    return send_from_directory(os.getcwd(), 'test_template.xlsx')


@gj_test.route('tests/add-many', methods=['GET', 'POST'])
def add_many_tests():
    form = TestListForm()
    if request.method == 'POST':
        filename = ''
        if form.upload.data:
            if not filename or (form.upload.data.filename != filename):
                upfile = form.upload.data
                filename = secure_filename(upfile.filename)
                upfile.save(filename)
            if upfile and allowed_file(upfile.filename):
                df = read_excel(upfile)
                for idx, rec in df.iterrows():
                    test_name, code, desc, prepare, specimen, specimen_quantity, unit, specimen_container, \
                    specimen_transportation, drop_off_location, solution, waiting_period, reporting_referral_values, \
                    interference_analysis, caution, test_location = rec

                    test_ = GJTest.query.filter_by(code=code).first()
                    if not test_:
                        new_test = GJTest(
                            test_name=test_name,
                            code=code,
                            desc=desc,
                            prepare=prepare,
                            specimen=specimen,
                            specimen_quantity=specimen_quantity,
                            unit=unit,
                            specimen_container=specimen_container,
                            specimen_transportation=specimen_transportation,
                            drop_off_location=drop_off_location,
                            solution=solution,
                            waiting_period=waiting_period,
                            reporting_referral_values=reporting_referral_values,
                            interference_analysis=interference_analysis,
                            caution=caution,
                            test_location=test_location
                        )
                        db.session.add(new_test)
                        db.session.commit()
                        flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
                return redirect(url_for('gj_test.view_tests'))

        flash('The file has been uploaded', 'success')
    else:
        for er in form.errors:
            flash(er, 'danger')
    return render_template('gj_test/tests_upload.html', form=form)
