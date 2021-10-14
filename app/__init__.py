from flask import Flask
from flask_restful import Api
from app.resources import configure_apis
from app.core.db_base import configure_db
from app.core.config import db_uri


def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='./static')
    app.secret_key = "$tajny_klic#"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    configure_db(app)
    configure_apis(Api(app))
    return app
