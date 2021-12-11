from app.core.model.models import AthleteModel, AthleteRoleModel
from app.core.db_base import session
from sqlalchemy import exc as e
from werkzeug.security import check_password_hash
from datetime import datetime

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
    def fetch_verified(data: dict):
        athlete = AthleteHandler.fetch(email=data['email'])
        if athlete is None:
            return None

        valid_password = check_password_hash(athlete.password_hash, data['password'])
        return athlete if valid_password else None

    @staticmethod
    def fetch_roles(athlete_id: int):
        return AthleteRoleModel.query.filter(AthleteRoleModel.roles_assigned.any(id=athlete_id)).all()

    @staticmethod
    def add(data: dict):
        if AthleteHandler.fetch(email=data['email']):
            return {"message": 'Athlete with registration email \'{}\' already exists!'.format(data['email'])}, 400

        athlete = AthleteModel(data['email'], data['password'], data['name'], data['perf_level'])

        # Every registered athlete is a user
        user_role = AthleteRoleModel.query.filter_by(id=1).first()
        athlete.roles.append(user_role)
        for role_id in data['roles']:
            role = AthleteRoleModel.query.filter_by(id=role_id) \
                .first_or_404(description='Role with id={} is not available'.format(role_id))
            athlete.roles.append(role)

        try:
            session.add(athlete)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An internal error occurred during registration, please try again!"}, 500
        return AthleteHandler.json_full(athlete), 201

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
        roles = AthleteHandler.fetch_roles(athlete.id)
        athlete_json['roles'] = []
        [athlete_json['roles'].append(role.id) for role in roles]
        return athlete_json

    @staticmethod
    def log_login(athlete: AthleteModel):
        athlete.last_login = datetime.now().replace(microsecond=0)