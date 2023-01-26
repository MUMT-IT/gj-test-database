# -*- coding:utf-8 -*-
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

test_specimen_assoc = db.Table('db_test_specimen_assoc_assoc',
                               db.Column('test_id', db.ForeignKey('gj_tests.id'), primary_key=True),
                               db.Column('specimen_id', db.ForeignKey('gj_test_specimens.id'), primary_key=True)
                               )

test_specimen_source_assoc = db.Table('db_test_specimen_source_assoc',
                                      db.Column('test_id', db.ForeignKey('gj_tests.id'), primary_key=True),
                                      db.Column('source_id', db.ForeignKey('gj_test_specimen_sources.id'),
                                                primary_key=True)
                                      )


class GJTest(db.Model):
    __tablename__ = 'gj_tests'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    test_name = db.Column('test_name', db.String(), info={'label': u'ชื่อการทดสอบ'})
    code = db.Column('code', db.String(), unique=True, info={'label': u'รหัส'})
    desc = db.Column('desc', db.Text(), info={'label': u'ข้อบ่งชี้ในการส่งตรวจ'})
    prepare = db.Column(db.Text(), info={'label': u'การเตรียมผู้ป่วย'})
    created_at = db.Column('created_at', db.DateTime(timezone=True), server_default=func.now())
    solution = db.Column('solution', db.String(), info={'label': u'วิธีการ/หลักการ'})
    test_date_id = db.Column('test_date_id', db.ForeignKey('gj_test_dates.id'))
    test_date = db.relationship('GJTestDate', backref=db.backref('test_dates', lazy='dynamic'))
    time_period_request_id = db.Column('time_period_request_id', db.ForeignKey('gj_test_time_period_requests.id'))
    time_period_request = db.relationship('GJTestTimePeriodRequest',
                                          backref=db.backref('time_period_requests', lazy='dynamic'))
    waiting_period_id = db.Column('waiting_period_id', db.ForeignKey('gj_test_waiting_periods.id'))
    waiting_period = db.relationship('GJTestWaitingPeriod', backref=db.backref('waiting_periods', lazy='dynamic'))
    reporting_referral_values = db.Column(db.Text(), info={'label': u'การรายงานผลและค่าอ้างอิง'})
    interference_analysis = db.Column(db.Text(), info={'label': u'สิ่งรบกวนต่อการตรวจวิเคราะห์'})
    caution = db.Column(db.String(), info={'label': u'ข้อควรระวังและอื่นๆ'})
    location_id = db.Column('location_id', db.ForeignKey('gj_test_locations.id'))
    test_location = db.relationship('GJTestLocation', foreign_keys=[location_id],
                                    backref=db.backref('test_locations', lazy='dynamic'))
    drop_off_location_id = db.Column('drop_off_location_id', db.ForeignKey('gj_test_locations.id'))
    drop_off_location = db.relationship('GJTestLocation', foreign_keys=[drop_off_location_id],
                                        backref=db.backref('location_drop_off', lazy='dynamic'))
    specimen_transportation_id = db.Column('specimen_transportation_id',
                                           db.ForeignKey('gj_test_specimen_transportations.id'))
    specimen_transportation = db.relationship('GJTestSpecimenTransportation', foreign_keys=[specimen_transportation_id],
                                              backref=db.backref('specimen_transportations', lazy='dynamic'))
    status = db.Column('status', db.String(),
                       info={'label': u'สถานะ', 'choices': [('None', '--Select Status--'),
                                                            ('Avaliable', 'Avaliable'),
                                                            ('Draft', 'Draft')]})
    specimens = db.relationship('GJTestSpecimen', secondary=test_specimen_assoc, lazy='subquery',
                                backref=db.backref('gjtests', lazy=True))
    quantity_id = db.Column('quantity_id', db.ForeignKey('gj_test_specimen_quantities.id'))
    quantity = db.relationship('GJTestSpecimenQuantity', foreign_keys=[quantity_id],
                               backref=db.backref('test_quantities', lazy='dynamic'))
    specimen_container_id = db.Column('specimen_container_id', db.ForeignKey('gj_test_specimen_containers.id'))
    specimen_container = db.relationship('GJTestSpecimenContainer', foreign_keys=[specimen_container_id],
                                         backref=db.backref('test_containers', lazy='dynamic'))
    specimens_source = db.relationship('GJTestSpecimenSource', secondary=test_specimen_source_assoc,
                                       lazy='subquery', backref=db.backref('specimens_sources', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test_name,
            'code': self.code,
            'desc': self.desc,
            'prepare': self.prepare,
            'specimens': ','.join([sp.specimen for sp in self.specimens]),
            'waiting_period': self.waiting_period.waiting_time_normal if self.waiting_period else '',
            'quantity': self.quantity.specimen_quantity if self.quantity else '',
            'solution': self.solution,
            'test_date': self.test_date.test_date if self.test_date else '',
            'reporting_referral_values': self.reporting_referral_values,
            'interference_analysis': self.interference_analysis,
            'caution': self.caution,
            'status': self.status
        }


class GJTestSpecimen(db.Model):
    __tablename__ = 'gj_test_specimens'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    specimen = db.Column('specimen', db.String(), info={'label': u'สิ่งส่งตรวจ'})

    def __str__(self):
        return u'{}'.format(self.specimen)

    def to_dict(self):
        return {
            'id': self.specimen,
            'text': self.specimen
        }


class GJTestSpecimenTransportation(db.Model):
    __tablename__ = 'gj_test_specimen_transportations'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    specimen_date_time = db.Column('specimen_date_time', db.String(),
                                   info={'label': u'วัน/เวลาการนำส่งสิ่งส่งตรวจ'})

    def __str__(self):
        return u'{}'.format(self.specimen_date_time)

    def to_dict(self):
        return {
            'id': self.specimen_date_time,
            'text': self.specimen_date_time
        }


class GJTestLocation(db.Model):
    __tablename__ = 'gj_test_locations'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    location = db.Column('location', db.String(), info={'label': u'สถานที่'})

    def __str__(self):
        return u'{}'.format(self.location)

    def to_dict(self):
        return {
            'id': self.location,
            'text': self.location
        }


class GJTestDate(db.Model):
    __tablename__ = 'gj_test_dates'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    test_date = db.Column('test_date', db.String(), info={'label': u'วันที่ทำการทดสอบ'})

    def __str__(self):
        return u'{}'.format(self.test_date)

    def to_dict(self):
        return {
            'id': self.test_date,
            'text': self.test_date
        }


class GJTestTimePeriodRequest(db.Model):
    __tablename__ = 'gj_test_time_period_requests'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    time_period_request = db.Column('time_period_request', db.String(),
                                    info={'label': u'ระยะเวลาที่สามารถขอตรวจเพิ่มได้'})

    def __str__(self):
        return u'{}'.format(self.time_period_request)

    def to_dict(self):
        return {
            'id': self.time_period_request,
            'text': self.time_period_request
        }


class GJTestWaitingPeriod(db.Model):
    __tablename__ = 'gj_test_waiting_periods'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    waiting_time_normal = db.Column('waiting_time_normal', db.String(), info={'label': u'ระยะเวลารอผล(ปกติ)'})
    waiting_time_urgent = db.Column('waiting_time_urgent', db.String(), info={'label': u'ระยะเวลารอผล(ด่วน)'})

    def __str__(self):
        return u'{}:{}'.format(self.waiting_time_normal, self.waiting_time_urgent)

    def normal_to_dict(self):
        return {
            'id': self.waiting_time_normal,
            'text': self.waiting_time_normal
        }

    def urgent_to_dict(self):
        return {
            'id': self.waiting_time_urgent,
            'text': self.waiting_time_urgent
        }


class GJTestSpecimenQuantity(db.Model):
    __tablename__ = 'gj_test_specimen_quantities'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    specimen_quantity = db.Column('specimen_quantity', db.String(), info={'label': u'ปริมาณสิ่งส่งตรวจ'})
    unit = db.Column('unit', db.String(), info={'label': u'หน่วย'})

    def __str__(self):
        return u'{} {}'.format(self.specimen_quantity, self.unit)

    def quantity_to_dict(self):
        return {
            'id': self.specimen_quantity,
            'text': self.specimen_quantity
        }

    def unit_to_dict(self):
        return {
            'id': self.unit,
            'text': self.unit
        }


class GJTestSpecimenContainer(db.Model):
    __tablename__ = 'gj_test_specimen_containers'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    specimen_container = db.Column('specimen_container', db.String(), info={'label': u'ภาชนะสิ่งส่งตรวจ'})

    def __str__(self):
        return u'{}'.format(self.specimen_container)

    def to_dict(self):
        return {
            'id': self.specimen_container,
            'text': self.specimen_container
        }


class GJTestSpecimenSource(db.Model):
    __tablename__ = 'gj_test_specimen_sources'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    specimens_id = db.Column('specimens_id', db.ForeignKey('gj_test_specimens.id'))
    specimens = db.relationship(GJTestSpecimen)
    specimen_quantity_id = db.Column('specimen_quantity_id', db.ForeignKey('gj_test_specimen_quantities.id'))
    specimen_quantity = db.relationship(GJTestSpecimenQuantity)
    specimen_container_id = db.Column('specimen_container_id', db.ForeignKey('gj_test_specimen_containers.id'))
    specimen_container = db.relationship(GJTestSpecimenContainer)

    def __str__(self):
        return u'{}:{}'.format(self.specimens, self.specimen_quantity, self.specimen_container)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
