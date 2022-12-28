# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_alchemy import model_form_factory, QuerySelectField

from app import db
from app.gj_test.models import *

BaseModelForm = model_form_factory(FlaskForm)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class TestListForm(ModelForm):
    class Meta:
        model = GJTest
        exclude = ['created_at']

    drop_off_location = QuerySelectField(u'สถานที่',
                                query_factory=lambda: GJTestLocation.query.all(),
                                blank_text='Select location..', allow_blank=False)
    specimen = QuerySelectField(u'สิ่งส่งตรวจ',
                                query_factory=lambda: GJTestSpecimen.query.all(),
                                blank_text='Select specimen..', allow_blank=False)
    test_date = QuerySelectField(u'วันที่ทำการทดสอบ',
                                query_factory=lambda: GJTestDate.query.all(),
                                blank_text='Select test date..', allow_blank=False)
    time_period_request = QuerySelectField(u'ระยะเวลารอผล',
                                query_factory=lambda: GJTestTimePeriodRequest.query.all(),
                                blank_text='Select time period request..', allow_blank=False)
    waiting_time = QuerySelectField(u'ระยะเวลารอผล',
                                           query_factory=lambda: GJTestWaitingPeriod.query.all(),
                                           blank_text='Select waiting time..', allow_blank=False)
    location_testing = QuerySelectField(u'สถานที่ทดสอบ',
                                query_factory=lambda: GJTestLocation.query.all(),
                                blank_text='Select location test..', allow_blank=False)


class LoginForm(ModelForm):
    email = StringField('Email',
            validators=[Length(min=10, message=u'สั้นเกินไป'),
                        Email(message=u'อีเมลไม่ถูกต้อง'), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Unknown email')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        return True


class RegisterForm(ModelForm):
    username = StringField('Username',
            validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email',
            validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField('Password',
            validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('Verify password',
            validators=[DataRequired(), EqualTo('password',
            message='Passwords must match')])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True