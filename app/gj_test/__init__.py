from flask import Blueprint

gj_test_bp = Blueprint('gj_test', __name__, url_prefix='/')

from . import views