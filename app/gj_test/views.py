import os
import logging
from flask import flash, redirect, url_for, render_template, request, jsonify, send_from_directory, session, \
    make_response
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from flask_wtf.csrf import generate_csrf
from itsdangerous import TimedJSONWebSignatureSerializer
from pandas import read_excel, DataFrame
from werkzeug.utils import secure_filename

from app import app, mail

from . import gj_test_bp as gj_test

from .models import *
from .forms import TestListForm, LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from functools import wraps

ALLOWED_EXTENSIONS = ['xlsx', 'xls']

logger = logging.getLogger('client')


def send_mail(recp, title, message):
    message = Message(subject=title, body=message, recipients=recp)
    mail.send(message)


def active_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            flash('You do not have permission to view access this page. Please contact admin!', 'warning')
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_function


@gj_test.route('/landing')
@active_user
@login_required
def landing():
    return render_template('gj_test/landing.html')


@gj_test.route('/index')
def index():
    return render_template('gj_test/index.html')


@gj_test.route('/')
def landing_for_admin():
    return render_template('gj_test/landing_for_admin.html')


def add_new_item_from_select(fieldname, model, attribute, attrname):
    value = request.form.get(fieldname)
    obj = model.query.filter(attribute == value).first()
    if not obj:
        obj = model()
        setattr(obj, attrname, value)
    return obj


@gj_test.route('/tests/specimens/add', methods=['POST'])
@gj_test.route('/tests/<int:test_id>/specimens/add', methods=['POST'])
@login_required
def add_specimens(test_id=None):
    specimens = request.form.get('specimens')
    specimen_container = request.form.get('specimen_container')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    if 'specimens_list' in session:
        session['specimens_list'].append((specimens, specimen_container, quantity, unit))
    else:
        session['specimens_list'] = [(specimens, specimen_container, quantity, unit)]

    resp = '<table class="table is-bordered is-fullwidth is-narrow">'
    resp += '''
        <thead>
        <th>ชนิด</th>
        <th>ภาชนะ</th>
        <th>ปริมาณ</th>
        <th></th>
        </thead>
        <tbody>
    '''
    for n, src in enumerate(session['specimens_list']):
        sp, c, q, u = src
        url = url_for('gj_test.delete_specimens', test_id=test_id, ind=n)
        resp += f'''
        <tr>
            <td>{sp}</td>
            <td>{c}</td>
            <td>{q} {u}</td>
            <td>
                <button class="button is-rounded is-small is-danger"
                        hx-headers='{{"X-CSRFToken": "{generate_csrf()}" }}'
                        hx-confirm="Are you sure you wish to delete this specimens source?"
                        hx-target="#specimen_list"
                        hx-swap="innerHTML"
                        hx-delete="{url}">
                    <span class="icon">
                        <i class="fas fa-trash-alt"></i>
                    </span>
                </button>
            </td>
        </tr>
        '''
    resp += '</tbody></table>'
    r = make_response(resp)
    r.headers['HX-Trigger'] = 'clearInput'
    return r


@gj_test.route('/tests/specimens-source/delete/<int:ind>', methods=['DELETE'])
@gj_test.route('/tests/<int:test_id>/specimens-source/delete/<int:ind>', methods=['DELETE'])
@login_required
def delete_specimens(ind, test_id=None):
    if test_id:
        test = GJTest.query.get(test_id)
        session['specimens_list'].pop(ind)
        for src in test.specimens_source:
            if src.to_tuple() not in session['specimens_list']:
                db.session.delete(src)
        db.session.commit()
    else:
        session['specimens_list'].pop(ind)
    resp = '<table class="table is-fullwidth is-bordered is-narrow">'
    resp += '''
            <thead>
            <th>ชนิด</th>
            <th>ภาชนะ</th>
            <th>ปริมาณ</th>
            <th></th>
            </thead>
            <tbody>
        '''
    for n, src in enumerate(session['specimens_list'], start=0):
        sp, c, q, u = src
        url = url_for('gj_test.delete_specimens', test_id=test_id, ind=n)
        resp += f'''
            <tr>
                <td>{sp}</td>
                <td>{c}</td>
                <td>{q} {u}</td>
                <td>
                    <button class="button is-rounded is-small is-danger"
                            hx-headers='{{"X-CSRFToken": "{generate_csrf()}" }}'
                            hx-confirm="Are you sure you wish to delete this specimens source?"
                            hx-target="#specimen_list"
                            hx-swap="innerHTML"
                            hx-delete="{url}">
                        <span class="icon">
                            <i class="fas fa-trash-alt"></i>
                        </span>
                    </button>
                </td>
            </tr>
            '''
    resp += '</tbody></table>'
    r = make_response(resp)
    r.headers['HX-Trigger'] = 'clearInput'
    return r


@gj_test.route('/new-test/add', methods=['GET', 'POST'])
@gj_test.route('/new-test/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def add_test(test_id=None):
    def add_specimens_source():
        for s, c, q, u in session['specimens_list']:
            specimen = GJTestSpecimen.query.filter_by(specimen=s).first()
            if not specimen:
                specimen = GJTestSpecimen(specimen=s)

            container = GJTestSpecimenContainer.query.filter_by(specimen_container=c).first()
            if not container:
                container = GJTestSpecimenContainer(specimen_container=c)

            quantity = GJTestSpecimenQuantity.query.filter_by(specimen_quantity=q).first()
            if not quantity:
                quantity = GJTestSpecimenQuantity(specimen_quantity=q)

            unit = GJTestSpecimenUnit.query.filter_by(specimens_unit=u).first()
            if not unit:
                unit = GJTestSpecimenUnit(specimens_unit=u)

            db.session.add(specimen)
            db.session.add(quantity)
            db.session.add(container)
            db.session.add(unit)
            db.session.commit()

            specimen_source_ = GJTestSpecimenSource.query.filter(GJTestSpecimenSource.specimens == specimen,
                                                                 GJTestSpecimenSource.specimen_quantity == quantity,
                                                                 GJTestSpecimenSource.specimens_unit == unit,
                                                                 GJTestSpecimenSource.specimen_container == container).first()
            if not specimen_source_:
                specimen_source_ = GJTestSpecimenSource(specimens=specimen,
                                                        specimen_quantity=quantity,
                                                        specimens_unit=unit,
                                                        specimen_container=container)
            yield specimen_source_

    if request.method == 'GET':
        session['specimens_list'] = []
    if test_id:
        test = GJTest.query.get(test_id)
        form = TestListForm(obj=test)
        for source in test.specimens_source:
            session['specimens_list'].append(source.to_tuple())
    else:
        form = TestListForm()
        test = None

    if form.validate_on_submit():
        if not test_id:
            new_test = GJTest()
            form.populate_obj(new_test)
            for source in add_specimens_source():
                new_test.specimens_source.append(source)
            del session['specimens_list']

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
            logger.info(f'ADD NEW TEST:{new_test.id}, {new_test.code} BY {current_user}')
            new_test.updater = current_user
            db.session.add(new_test)
            db.session.commit()
        else:
            form.populate_obj(test)
            test.updater = current_user
            logger.info(f'EDIT TEST:{test.id}, {test.code} BY {current_user}')
            for source in add_specimens_source():
                test.specimens_source.append(source)
            db.session.add(test)
            db.session.commit()
            del session['specimens_list']
        flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
        return redirect(url_for('gj_test.view_tests'))
    else:
        for er in form.errors:
            flash("{} {}".format(er, form.errors[er]), 'danger')
    return render_template('gj_test/new_test.html', form=form, url_next=request.referrer, test=test)


@gj_test.route('api/v1.0/specimens', methods=['GET'])
def get_all_specimens():
    specimens = [specimen.to_dict() for specimen in GJTestSpecimen.query.all()]
    return jsonify({'results': specimens})


@gj_test.route('api/v1.0/containers', methods=['GET'])
def get_all_containers():
    containers = [specimen_container.to_dict() for specimen_container in GJTestSpecimenContainer.query.all()]
    return jsonify({'results': containers})


@gj_test.route('api/v1.0/specimen_quantity', methods=['GET'])
def get_all_specimen_quantity():
    quantities = [specimen_quantity.to_dict() for specimen_quantity in GJTestSpecimenQuantity.query.all()]
    return jsonify({'results': quantities})


@gj_test.route('api/v1.0/specimens_unit', methods=['GET'])
def get_all_specimens_unit():
    units = [specimens_unit.to_dict() for specimens_unit in GJTestSpecimenUnit.query.all()]
    return jsonify({'results': units})


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
    time_period_requests = [time_period_request.to_dict() for time_period_request in
                            GJTestTimePeriodRequest.query.all()]
    return jsonify({'results': time_period_requests})


@gj_test.route('api/v1.0/test_locations', methods=['GET'])
def get_all_test_locations():
    test_locations = [location.to_dict() for location in GJTestLocation.query.all()]
    return jsonify({'results': test_locations})


@gj_test.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            password = form.password.data
            if user.verify_password(password):
                login_user(user, form.remember_me.data)
                app.logger.info('%s logged in successfully', user.username)
                return redirect(url_for('gj_test.landing'))
            else:
                flash(u'Wrong password, try again. รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง', 'danger')
                return redirect(url_for('gj_test.login'))
        else:
            flash(u'User does not exists. ไม่พบบัญชีผู้ใช้ในระบบ', 'danger')
            return redirect(url_for('gj_test.register'))

    return render_template('gj_test/login.html', form=form, errors=form.errors)


@gj_test.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('gj_test.login'))


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
            try:
                send_mail(['{}'.format(form.email.data)],
                          title='MUMT-GJ: Password Reset. ตั้งรหัสผ่านใหม่สำหรับระบบ MUMT-GJ',
                          message=message)
            except Exception as e:
                flash(u'Failed to send an email to {}. ระบบไม่สามารถส่งอีเมลได้กรุณาตรวจสอบอีกครั้ง' \
                      .format(form.email.data), 'danger')
            else:
                flash(u'Please check your email for the link to reset the password within 20 minutes.'
                      u' โปรดตรวจสอบอีเมลของท่านเพื่อทำการแก้ไขรหัสผ่านภายใน 20 นาที', 'success')
            return redirect(url_for('gj_test.login'))
    return render_template('gj_test/forgot_password.html', form=form, errors=form.errors)


@gj_test.route('/tests/view')
def view_tests():
    return render_template('gj_test/view_tests.html')


@gj_test.route('/api/view-tests')
def get_tests_view_data():
    query = GJTest.query
    search = request.args.get('search[value]')
    query = query.filter(db.or_(
        GJTest.test_name.ilike(u'%{}%'.format(search)),
        GJTest.code.ilike(u'%{}%'.format(search)),

    ))
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for test in query:
        test_data = test.to_dict()
        test_data['view'] = '<a href="{}" class="button is-small is-rounded is-info is-outlined">ดูข้อมูล</a>' \
            .format(url_for('gj_test.view_info_test', test_id=test.id))
        data.append(test_data)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': GJTest.query.count(),
                    'draw': request.args.get('draw', type=int),
                    })


@gj_test.route('/info-tests/view/<int:test_id>')
@gj_test.route('/info-tests/view/<int:test_id>/revisions/<int:revision_index>')
def view_info_test(test_id, revision_index=None):
    test = GJTest.query.get(test_id)
    if revision_index:
        test = test.versions[revision_index]
    return render_template('gj_test/view_info_test.html', test=test, revision_index=revision_index)


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
@login_required
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
            df = df.fillna("")
            for idx, rec in df.iterrows():
                no, test_name, code, desc, prepare, specimen, specimen_quantity, specimens_unit, specimen_container, \
                specimen_date_time, drop_off_location, method, test_date, waiting_time_normal, waiting_time_urgent, \
                reporting_referral_values, time_period_request, interference_analysis, caution, test_location = rec

                specimen_obj = GJTestSpecimen.query.filter_by(specimen=specimen).first()
                if not specimen_obj:
                    specimen_obj = GJTestSpecimen(specimen=specimen)
                    db.session.add(specimen_obj)
                    db.session.commit()

                specimen_container_obj = GJTestSpecimenContainer.query.filter_by(
                    specimen_container=specimen_container).first()
                if not specimen_container_obj:
                    specimen_container_obj = GJTestSpecimenContainer(specimen_container=specimen_container)
                    db.session.add(specimen_container_obj)
                    db.session.commit()

                specimen_quantity = str(specimen_quantity)
                specimen_quantity_obj = GJTestSpecimenQuantity.query.filter_by(
                    specimen_quantity=specimen_quantity).first()
                if not specimen_quantity_obj:
                    specimen_quantity_obj = GJTestSpecimenQuantity(specimen_quantity=specimen_quantity)
                    db.session.add(specimen_quantity_obj)
                    db.session.commit()

                unit_obj = GJTestSpecimenUnit.query.filter_by(specimens_unit=specimens_unit).first()
                if not unit_obj:
                    unit_obj = GJTestSpecimenUnit(specimens_unit=specimens_unit)
                    db.session.add(unit_obj)
                    db.session.commit()

                specimen_transportation_ = GJTestSpecimenTransportation.query.filter_by(
                    specimen_date_time=specimen_date_time).first()
                if not specimen_transportation_:
                    specimen_transportation_ = GJTestSpecimenTransportation(specimen_date_time=specimen_date_time)

                drop_off_location_ = GJTestLocation.query.filter_by(location=drop_off_location).first()
                if not drop_off_location_:
                    drop_off_location_ = GJTestLocation(location=drop_off_location)

                test_date_ = GJTestDate.query.filter_by(test_date=test_date).first()
                if not test_date_:
                    test_date_ = GJTestDate(test_date=test_date)

                waiting_time = GJTestWaitingPeriod.query.filter_by(waiting_time_normal=waiting_time_normal,
                                                                   waiting_time_urgent=waiting_time_urgent).first()
                if not waiting_time:
                    waiting_time = GJTestWaitingPeriod(waiting_time_normal=waiting_time_normal,
                                                       waiting_time_urgent=waiting_time_urgent)

                time_period_request_ = GJTestTimePeriodRequest.query.filter_by(
                    time_period_request=time_period_request).first()
                if not time_period_request_:
                    time_period_request_ = GJTestTimePeriodRequest(time_period_request=time_period_request)

                test_location_ = GJTestLocation.query.filter_by(location=test_location).first()
                if not test_location_:
                    test_location_ = GJTestLocation(location=test_location)

                specimen_source_ = GJTestSpecimenSource.query.filter_by(specimens=specimen_obj,
                                                                        specimen_quantity=specimen_quantity_obj,
                                                                        specimens_unit=unit_obj,
                                                                        specimen_container=specimen_container_obj).first()
                if not specimen_source_:
                    specimen_source_ = GJTestSpecimenSource(specimens=specimen_obj,
                                                            specimen_quantity=specimen_quantity_obj,
                                                            specimens_unit=unit_obj,
                                                            specimen_container=specimen_container_obj)
                    db.session.add(specimen_source_)
                    db.session.commit()

                test_ = GJTest.query.filter_by(code=code).first()
                if not test_:
                    new_test = GJTest(
                        test_name=test_name,
                        code=code,
                        desc=desc,
                        prepare=prepare,
                        specimen_transportation=specimen_transportation_,
                        drop_off_location=drop_off_location_,
                        solution=method,
                        test_date=test_date_,
                        waiting_period=waiting_time,
                        reporting_referral_values=reporting_referral_values,
                        time_period_request=time_period_request_,
                        interference_analysis=interference_analysis,
                        caution=caution,
                        test_location=test_location_
                    )
                    new_test.specimens_source.append(specimen_source_)
                    db.session.add(new_test)
                    db.session.commit()
                else:
                    if specimen_source_ not in test_.specimens_source:
                        test_.specimens_source.append(specimen_source_)
                    db.session.add(test_)
                    db.session.commit()
            flash(u'บันทึกข้อมูลสำเร็จ.', 'success')
            logger.info(f'UPLOAD TEST BY {current_user}')
            return redirect(url_for('gj_test.view_tests'))
    else:
        for er in form.errors:
            flash(er, 'danger')
    return render_template('gj_test/tests_upload.html', form=form)


@gj_test.route('/tests/<int:test_id>/delete')
@login_required
def delete_test(test_id):
    if test_id:
        test = GJTest.query.get(test_id)
        flash(u'Test has been removed.', 'danger')
        logger.info(f'DELETE TEST:{test.id}, {test.code} BY {current_user}')
        db.session.delete(test)
        db.session.commit()
        return redirect(url_for('gj_test.view_tests', test_id=test_id))
