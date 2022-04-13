from flask_jwt_extended import create_access_token

from app.core.model.models import AthleteModel, AthleteRoleModel, AthleteRoleAssociationModel
from app.core.db_base import session
from sqlalchemy import exc as e
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import current_app as app

import re


def validate_email(email: str):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return True if re.fullmatch(email_regex, email) else False


class AthleteHandler:
    @staticmethod
    def fetch_all():
        return AthleteModel.query.all()

    @staticmethod
    def fetch(**kwargs):
        if 'id' in kwargs:
            return AthleteModel.query.filter_by(id=kwargs.get('id')).first()
        elif 'email' in kwargs:
            return AthleteModel.query.filter_by(email=kwargs.get('email')).first()
        else:
            raise ValueError("Unexpected argument has been provided to the fetch function - expected 'id' or 'login'")

    @staticmethod
    def fetch_page(page_id: int, per_page: int):
        players_page = AthleteModel.query.paginate(page_id, per_page, error_out=False).items
        next_page_id = None if len(players_page) < per_page else page_id + 1
        prev_page_id = None if page_id == 1 else page_id - 1
        return players_page, next_page_id, prev_page_id

    @staticmethod
    def fetch_verified(data: dict):
        athlete = AthleteHandler.fetch(email=data['email'])
        if athlete is None:
            return None

        valid_password = check_password_hash(athlete.password_hash, data['password'])
        return athlete if valid_password else None

    @staticmethod
    def fetch_roles(athlete_id: int):
        return AthleteRoleAssociationModel.query.filter(AthleteRoleAssociationModel.roles_assigned.has(id=athlete_id)).all()

    @staticmethod
    def add(data: dict):
        if validate_email(data['email']):
            athlete = AthleteModel(data['email'], data['password'])
        else:
            error_text = 'Provided e-mail \'{}\' is not an email!'.format(data['email'])
            app.logger.error(error_text + ' Returning 400.')
            return {"message": error_text}, 400

        if AthleteHandler.fetch(email=data['email']):
            error_text = 'Uživatel registrovaný pod e-mailem \'{}\' již existuje!'.format(data['email'])
            app.logger.error(error_text + ' Returning 400.')
            return {"message": error_text}, 400

        # Every registered athlete is a user
        # user_role = AthleteRoleModel.query.filter_by(id=1).first()
        # athlete.roles.append(user_role)
        # for role_id in data['roles']:
        #     role = AthleteRoleModel.query.filter_by(id=role_id) \
        #         .first_or_404(description='Role with id={} is not available'.format(role_id))
            # athlete.roles.append(role)

        try:
            session.add(athlete)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An internal error occurred during registration, please try again!"}, 500

        return {
            'access_token': create_access_token(identity=data['email']),
            'athlete': AthleteHandler.json_full(athlete)
        }
        # return AthleteHandler.json_full(athlete), 201

    @staticmethod
    def delete(athlete_id: int):
        athlete = AthleteHandler.fetch(id=athlete_id)
        session.delete(athlete)
        session.commit()
        return {'message': 'Athlete has been deleted'}, 204

    @staticmethod
    def update(athlete_id: int, data: dict):
        athlete = AthleteHandler.fetch(id=athlete_id)
        athlete.__dict__.update(data)
        session.commit()
        return athlete.json()

    @staticmethod
    def json_full(athlete: AthleteModel):
        athlete_json = athlete.json()
        athlete_roles = AthleteHandler.fetch_roles(athlete.id)
        athlete_json['roles'] = []
        for athlete_role in athlete_roles:
            role = {'id': athlete_role.role_id, 'skill_level': athlete_role.skill_level}
            athlete_json['roles'].append(role)
        return athlete_json

    @staticmethod
    def log_login(athlete: AthleteModel):
        athlete.last_login = datetime.now().replace(microsecond=0)
