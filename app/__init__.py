import os

from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import timedelta

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated


load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=20)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('MUMT-GJ',
                                     os.environ.get('MAIL_USERNAME'))


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"
csrf = CSRFProtect(app)
admin = Admin(app)
mail = Mail(app)


from . import gj_test

app.register_blueprint(gj_test.gj_test_bp)
from app.gj_test import models

from .gj_test.models import *


admin.add_views(ModelView(GJTest, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestSpecimen, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestSpecimenQuantity, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestSpecimenTransportation, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestLocation, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestDate, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestTimePeriodRequest, db.session, category='GJ Test'))
admin.add_views(ModelView(GJTestWaitingPeriod, db.session, category='GJ Test'))
admin.add_views(ModelView(User, db.session, category='GJ Test'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))