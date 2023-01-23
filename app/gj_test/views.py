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
from .forms import TestListForm, LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from .. import csrf

ALLOWED_EXTENSIONS = ['xlsx', 'xls']


def send_mail(recp, title, message):
    message = Message(subject=title, body=message, recipients=recp)
    mail.send(message)


@gj_test.route('/landing')
def landing():
    return render_template('gj_test/landing.html')


def add_new_item_from_select(fieldname, model, attribute, attrname):
    value = request.form.get(fieldname)
    obj = model.query.filter(attribute==value).first()
    if not obj:
        obj = model()
        setattr(obj, attrname, value)
    return obj


@gj_test.route('/new-test/add', methods=['GET', 'POST'])
def add_test():
    form = TestListForm()
    if form.validate_on_submit():
        new_test = GJTest()
        form.populate_obj(new_test)
        for text in request.form.getlist('specimens'):
            specimen = GJTestSpecimen.query.filter_by(specimen=text).first()
            if specimen:
                new_test.specimens.append(specimen)
            else:
                specimen = GJTestSpecimen(specimen=text)
                new_test.specimens.append(specimen)
        quantity_value = request.form.get('quantity')
        unit_value = request.form.get('unit')
        specimen_quantity_and_unit = GJTestSpecimenQuantity.query.filter_by(specimen_quantity=quantity_value,
                                                                            unit=unit_value).first()
        if not specimen_quantity_and_unit:
            specimen_quantity_and_unit = GJTestSpecimenQuantity(specimen_quantity=quantity_value,
                                                                unit=unit_value)
        new_test.quantity = specimen_quantity_and_unit

        transport_date_time = add_new_item_from_select('specimen_transportation',
                                                       GJTestSpecimenTransportation,
                                                       GJTestSpecimenTransportation.specimen_date_time,
                                                       'specimen_date_time')
        new_test.specimen_transportation = transport_date_time

        drop_off_location_ = add_new_item_from_select('drop_off_location',
                                                      GJTestLocation,
                                                      GJTestLocation.location,
                                                      'location')
        new_test.drop_off_location = drop_off_location_

        test_date_ = add_new_item_from_select('test_date',
                                              GJTestDate,
                                              GJTestDate.test_date,
                                              'test_date')
        new_test.test_date = test_date_

        normal_waiting_time_value = request.form.get('normal_waiting_time')
        urgent_waiting_time_value = request.form.get('urgent_waiting_time')
        waiting_time = GJTestWaitingPeriod.query.filter_by(waiting_time_normal=normal_waiting_time_value,
                                                           waiting_time_urgent=urgent_waiting_time_value).first()
        if not waiting_time:
            waiting_time = GJTestWaitingPeriod(waiting_time_normal=normal_waiting_time_value,
                                               waiting_time_urgent=urgent_waiting_time_value)
        new_test.waiting_period = waiting_time

        time_period_request_ = add_new_item_from_select('time_period_request',
                                                        GJTestTimePeriodRequest,
                                                        GJTestTimePeriodRequest.time_period_request,
                                                        'time_period_request')
        new_test.time_period_request = time_period_request_

        test_location_ = add_new_item_from_select('test_location',
                                                      GJTestLocation,
                                                      GJTestLocation.location,
                                                      'location')
        new_test.test_location = test_location_

        db.session.add(new_test)
        db.session.commit()
        flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
        return redirect(url_for('gj_test.view_tests'))
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('gj_test/new_test.html', form=form, url_next=request.referrer)


@gj_test.route('api/v1.0/specimens', methods=['GET'])
def get_all_specimens():
    specimens = [specimen.to_dict() for specimen in GJTestSpecimen.query.all()]
    return jsonify({'results': specimens})


@gj_test.route('api/v1.0/specimen_quantity_and_unit/<mode>')
def get_all_specimen_quantity_and_unit(mode):
    if mode == "specimen_quantity":
        data = [q.quantity_to_dict() for q in GJTestSpecimenQuantity.query.all()]
    else:
        data = [q.unit_to_dict() for q in GJTestSpecimenQuantity.query.all()]
    return jsonify({'results': data})


@gj_test.route('api/v1.0/specimen_transportations', methods=['GET'])
def get_all_specimen_transportations():
    specimen_transportations = [specimen_transportation.to_dict() for specimen_transportation in
                                GJTestSpecimenTransportation.query.all()]
    return jsonify({'results': specimen_transportations})


@gj_test.route('api/v1.0/drop_off_locations', methods=['GET'])
def get_all_drop_off_locations():
    drop_off_locations = [location.to_dict() for location in GJTestLocation.query.all()]
    return jsonify({'results': drop_off_locations})


@gj_test.route('api/v1.0/test_dates', methods=['GET'])
def get_all_test_dates():
    test_dates = [test_date.to_dict() for test_date in GJTestDate.query.all()]
    return jsonify({'results': test_dates})


@gj_test.route('api/v1.0/waiting_time/<mode>')
def get_all_waiting_time(mode):
    if mode == "normal":
        data = [w.normal_to_dict() for w in GJTestWaitingPeriod.query.all()]
    else:
        data = [w.urgent_to_dict() for w in GJTestWaitingPeriod.query.all()]
    return jsonify({'results': data})


@gj_test.route('api/v1.0/time_period_requests', methods=['GET'])
def get_all_time_period_requests():
    time_period_requests = [time_period_request.to_dict() for time_period_request in GJTestTimePeriodRequest.query.all()]
    return jsonify({'results': time_period_requests})


@gj_test.route('api/v1.0/test_locations', methods=['GET'])
def get_all_test_locations():
    test_locations = [location.to_dict() for location in GJTestLocation.query.all()]
    return jsonify({'results': test_locations})


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
        # test_data['edit'] = '<a href="{}" class="button is-small is-danger is-outlined">แก้ไขข้อมูล </a>'.format(
        #     url_for('gj_test.edit_test', test_id=test.id))
        data.append(test_data)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': GJTest.query.count(),
                    'draw': request.args.get('draw', type=int),
                    })


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
        if not filename or (form.upload.data.filename != filename):
            upfile = form.upload.data
            filename = secure_filename(upfile.filename)
            upfile.save(filename)
        if upfile and allowed_file(upfile.filename):
            df = read_excel(upfile)
            for idx, rec in df.iterrows():
                no, test_name, code, desc, prepare, specimen, specimen_quantity, unit, specimen_container, \
                specimen_transportation, drop_off_location, method, test_date, waiting_time_normal, waiting_time_urgent,\
                reporting_referral_values, interference_analysis, time_period_request, caution, test_location = rec

                specimens = GJTestSpecimen.query.filter_by(specimen=specimen).first()
                if not specimens:
                    specimens = GJTestSpecimen(specimen=specimen)

                waiting_time = GJTestWaitingPeriod.query.filter_by(waiting_time_normal=waiting_time_normal,
                                                                   waiting_time_urgent=waiting_time_urgent)
                if not waiting_time:
                    waiting_time = GJTestWaitingPeriod(waiting_time_normal=waiting_time_normal,
                                                       waiting_time_urgent=waiting_time_urgent)

                test_ = GJTest.query.filter_by(code=code).first()
                if not test_:
                    new_test = GJTest(
                        test_name=test_name,
                        code=code,
                        desc=desc,
                        prepare=prepare,
                        specimens=specimens,
                        specimen_quantity=specimen_quantity,
                        unit=unit,
                        specimen_container=specimen_container,
                        specimen_transportation=specimen_transportation,
                        drop_off_location=drop_off_location,
                        solution=method,
                        waiting_period=waiting_time,
                        reporting_referral_values=reporting_referral_values,
                        interference_analysis=interference_analysis,
                        caution=caution,
                        test_location=test_location
                    )
                    db.session.add(new_test)
                    db.session.commit()
                    flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
            return redirect(url_for('gj_test.view_tests'))
    else:
        for er in form.errors:
            flash(er, 'danger')
    return render_template('gj_test/tests_upload.html', form=form)
