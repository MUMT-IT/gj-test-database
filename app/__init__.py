import os
from functools import wraps

from flask import Flask, flash, redirect
from dotenv import load_dotenv
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import timedelta


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith('postgresql'):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=20)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('MUMT-GJ',
                                     os.environ.get('MAIL_USERNAME'))
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "gj_test.login"
csrf = CSRFProtect(app)
admin = Admin(app, index_view=MyAdminIndexView())
mail = Mail(app)
Session(app)

from app.gj_test import gj_test_bp

app.register_blueprint(gj_test_bp)

from app.gj_test.models import *

admin.add_views(ModelView(GJTest, db.session, category='Test'))
admin.add_views(ModelView(GJTestSpecimen, db.session, category='Test'))
admin.add_views(ModelView(GJTestSpecimenQuantity, db.session, category='Test'))
admin.add_views(ModelView(GJTestSpecimenUnit, db.session, category='Test'))
admin.add_views(ModelView(GJTestSpecimenContainer, db.session, category='Test'))
admin.add_views(ModelView(GJTestSpecimenTransportation, db.session, category='Test'))
admin.add_views(ModelView(GJTestLocation, db.session, category='Test'))
admin.add_views(ModelView(GJTestDate, db.session, category='Test'))
admin.add_views(ModelView(GJTestTimePeriodRequest, db.session, category='Test'))
admin.add_views(ModelView(GJTestWaitingPeriod, db.session, category='Test'))
admin.add_views(ModelView(User, db.session, category='User'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def active_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_active:
            flash('You do not have permission to view access this page.', 'warning')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function
