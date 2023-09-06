# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets, StringField, PasswordField, BooleanField, SubmitField, FileField,\
    TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_alchemy import model_form_factory

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

    upload = FileField(u'อัพโหลดไฟล์')
    outsource_lab_test_url = TextAreaField('URL for Outsource Lab Test')
    request_form_url = TextAreaField('URL for Request Form')


class LoginForm(ModelForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Unknown username')
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
                            validators=[DataRequired(),
                                        EqualTo('password',
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


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    new_pass = PasswordField('New Password', validators=[DataRequired()])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_pass')])
    submit = SubmitField('Submit')


class SpecimenForm(ModelForm):
    class Meta:
        model = GJTestSpecimen


# class LocationForm(ModelForm):
#     class Meta:
#         model = GJTestLocation


class TimePeriodRequestedForm(ModelForm):
    class Meta:
        model = GJTestTimePeriodRequest


class WaitingTimeForm(ModelForm):
    class Meta:
        model = GJTestWaitingPeriod


class TestDateForm(ModelForm):
    class Meta:
        model = GJTestDate


class SpecimenTransportationForm(ModelForm):
    class Meta:
        model = GJTestSpecimenTransportation
