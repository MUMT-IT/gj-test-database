# -*- coding:utf-8 -*-
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class GJTest(db.Model):
    __tablename__ = 'gj_tests'
    id = db.Column('id', db.Integer, primary_key=True)
    test_name = db.Column('test_name', db.String(), info={'label': u'ชื่อการทดสอบ'})
    code = db.Column('code', db.String(), unique=True, info={'label': u'รหัส'})
    desc = db.Column('desc', db.Text(), info={'label': u'ข้อบ่งชี้ในการส่งตรวจ'})
    prepare = db.Column(db.Text(), info={'label': u'การเตรียมผู้ป่วย'})
    specimen_id = db.Column('specimen_id', db.ForeignKey('gj_test_specimens.id'))
    specimen = db.relationship('GJTestSpecimen', backref=db.backref('specimen_test', lazy='dynamic'))
    created_at = db.Column('created_at', db.DateTime(timezone=True), server_default=func.now())
    solution = db.Column('solution', db.String(), info={'label': u'วิธีการ/หลักการ'})
    test_date_id = db.Column('test_date_id', db.ForeignKey('gj_test_dates.id'))
    test_date = db.relationship('GJTestDate', backref=db.backref('test_dates', lazy='dynamic'))
    time_period_request_id = db.Column('time_period_request_id', db.ForeignKey('gj_test_time_period_requests.id'))
    time_period_request = db.relationship('GJTestTimePeriodRequest', backref=db.backref('time_period_requests', lazy='dynamic'))
    waiting_period_id = db.Column('waiting_period_id', db.ForeignKey('gj_test_waiting_periods.id'))
    waiting_period = db.relationship('GJTestWaitingPeriod', backref=db.backref('waiting_periods', lazy='dynamic'))
    reporting_referral_values = db.Column(db.String(), info={'label': u'การรายงานผลและค่าอ้างอิง'})
    interference_analysis = db.Column(db.String(), info={'label': u'สิ่งรบกวนต่อการตรวจวิเคราะห์'})
    caution = db.Column(db.String(), info={'label': u'ข้อควรระวังและอื่นๆ'})
    location_id = db.Column('location_id', db.ForeignKey('gj_test_locations.id'))
    test_location = db.relationship('GJTestLocation', foreign_keys=[location_id],
                                    backref=db.backref('test_locations', lazy='dynamic'))
    drop_off_location_id = db.Column('drop_off_location_id', db.ForeignKey('gj_test_locations.id'))
    drop_off_location = db.relationship('GJTestLocation', foreign_keys=[drop_off_location_id],
                                        backref=db.backref('location_drop_off', lazy='dynamic'))
    status = db.Column('status', db.String(),
                     info={'label': u'สถานะ', 'choices': [('None', u'--โปรดเลือกสถานะ--'),
                                                          ('Avaliable', 'Avaliable'),
                                                          ('Draft', 'Draft')]})

    def __str__(self):
        return u'{}: {}'.format(self.specimen, self.test_date, self.test_location)

    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test_name,
            'code': self.code,
            'desc': self.desc,
            'prepare': self.prepare,
            'specimen': self.specimen,
            'solution': self.solution,
            'test_date': self.test_date,
            'time_period_request': self.time_period_request,
            'waiting_period': self.waiting_period,
            'reporting_referral_values': self.reporting_referral_values,
            'interference_analysis': self.interference_analysis,
            'caution': self.caution,
            'test_location': self.test_location,
            'drop_off_location': self.drop_off_location,
            'status': self.status
        }


class GJTestSpecimen(db.Model):
    __tablename__ = 'gj_test_specimens'
    id = db.Column('id', db.Integer, primary_key=True)
    specimen = db.Column('specimen', db.String(), info={'label': u'สิ่งส่งตรวจ'})
    specimen_quantity = db.Column('specimen_quantity', db.String(), info={'label': u'ปริมาณสิ่งส่งตรวจ'})
    specimen_container = db.Column('specimen_container', db.String(), info={'label': u'ภาชนะสิ่งส่งตรวจ'})
    unit = db.Column('unit', db.String(),
                     info={'label': u'หน่วย', 'choices': [('None', u'--โปรดเลือกหน่วย--'),
                                                          ('g', 'g'),
                                                          ('mL', 'mL')]})


    def __str__(self):
        return u'{}'.format(self.specimen)


class GJTestSpecimenTransportation(db.Model):
    __tablename__ = 'gj_test_specimen_transportations'
    id = db.Column('id', db.Integer, primary_key=True)
    specimen_date_time = db.Column('specimen_date_time', db.String(),
                                   info={'label': u'วัน/เวลาการนำส่งสิ่งส่งตรวจ',
                                         'choices': [('None', u'--โปรดเลือกวัน/เวลา--'),
                                                     (u'ทุกวันตลอด 24 ชั่วโมง', 'ทุกวันตลอด 24 ชั่วโมง'),
                                                     (u'ทุกวัน', 'ทุกวัน'),
                                                     (u'วัน/เวลา', 'วัน/เวลา')]})
    location_id = db.Column('location_id', db.ForeignKey('gj_test_locations.id'))
    location = db.relationship('GJTestLocation', backref=db.backref('location_specimens', lazy='dynamic'))


class GJTestLocation(db.Model):
    __tablename__ = 'gj_test_locations'
    id = db.Column('id', db.Integer, primary_key=True)
    location = db.Column('location', db.String(), info={'label': u'สถานที่'})

    def __str__(self):
        return u'{}'.format(self.location)


class GJTestDate(db.Model):
    __tablename__ = 'gj_test_dates'
    id = db.Column('id', db.Integer, primary_key=True)
    test_date = db.Column('test_date', db.String(), info={'label': u'วันที่ทำการทดสอบ'})

    def __str__(self):
        return u'{}'.format(self.test_date)


class GJTestTimePeriodRequest(db.Model):
    __tablename__ = 'gj_test_time_period_requests'
    id = db.Column('id', db.Integer, primary_key=True)
    time_period_request = db.Column('time_period_request', db.String(), info={'label': u'ระยะเวลาที่สามารถขอตรวจเพิ่มได้'})

    def __str__(self):
        return u'{}'.format(self.time_period_request)


class GJTestWaitingPeriod(db.Model):
    __tablename__ = 'gj_test_waiting_periods'
    id = db.Column('id', db.Integer, primary_key=True)
    waiting_time_normal = db.Column('waiting_time_normal', db.String(), info={'label': u'ระยะเวลารอผล(ปกติ)'})
    waiting_time_urgent = db.Column('waiting_time_urgent', db.String(), info={'label': u'ระยะเวลารอผล(ด่วน)'})

    def __str__(self):
        return u'{}:{}'.format(self.waiting_time_normal, self.waiting_time_urgent)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, index=True)
    username = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


