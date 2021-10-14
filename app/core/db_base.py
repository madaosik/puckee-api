from app.core.model.models import sqlDb
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

session = sqlDb.session


def configure_db(app):
    db = SQLAlchemy(app)
    Migrate(app, db)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()
