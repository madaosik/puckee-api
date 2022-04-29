from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.resources import configure_apis
from app.core.db_base import configure_db
from app.core.config import DB_URI, SECRET_KEY
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='./static')
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # JWT authentication setup
    app.config["JWT_SECRET_KEY"] = SECRET_KEY
    JWTManager(app)
    # Added to return 401 Unauthorized even outside of debug mode
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['BUNDLE_ERRORS'] = True

    configure_db(app)
    configure_apis(Api(app))
    return app
