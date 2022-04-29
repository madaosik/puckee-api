from flask_jwt_extended import create_access_token

from app.core.model.models import AthleteModel, AthleteRoleModel, AthleteRoleAssociationModel, FollowersModel, \
    AnonymousAthleteModel
from app.core.db_base import session
from sqlalchemy import exc as e
from sqlalchemy.sql.expression import false, true
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import current_app as app
import re


def validate_email(email: str):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return True if re.fullmatch(email_regex, email) else False


class AnonymousAthleteHandler:
    @staticmethod
    def fetch(name: str, added_in: int, requesting_id: int):
        """
        Fetches an existing anonymous athlete based on his name or creates a new one if not exists
        @param name: str
        @param added_in: int ID of the game where the athlete is required
        @param requesting_id: id
        """
        athlete = AnonymousAthleteModel.query.filter_by(name=name).first()
        if athlete:
            return athlete

        athlete = AnonymousAthleteModel(name, added_in, requesting_id)
        try:
            session.add(athlete)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An internal error occurred during registration, please try again!"}, 500

        return athlete

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
    def fetch_anonymous(name: str):
        return AnonymousAthleteModel.query.filter_by(name=name).first()

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
    def fetch_followers(athlete_id: int, role_id=None, opt_out_mode=None):
        """
        Fetches all followers of a given 'athlete_id' - optionally restricted by the `role_id` and 'opt_out_mode' parameter.

        @param athlete_id: ID of athlete for which the followers are being gathered
        @param role_id: ID of the searched role
        @param opt_out_mode: true for opt_out_mode == 'true', false otherwise

        @return [AthleteModel]
        """
        if not role_id:
            return FollowersModel.query.filter(FollowersModel.followee.has(id=athlete_id)).all()

        if opt_out_mode:
            return FollowersModel.query.filter(FollowersModel.followee.has(id=athlete_id),
                                               FollowersModel.follower.has(AthleteModel.roles.any(role_id=role_id)),
                                               FollowersModel.opt_out_mode == opt_out_mode).all()
        else:
            return FollowersModel.query.filter(FollowersModel.followee.has(id=athlete_id),
                                               AthleteModel.roles.any(role_id=role_id)).all()

    @staticmethod
    def follow_status(follower_id, followee_id):
        """
        Checks if 'analyzed_id' follows 'requested_id'
        @return FollowersModel
        """
        # Athlete I follow
        return FollowersModel.query\
            .filter(FollowersModel.follower.has(id=follower_id))\
            .filter(FollowersModel.followee.has(id=followee_id))\
            .first()

    @staticmethod
    def add_follower_status(athlete_json: dict, follower_id: int, followee_id: int):
        """
        Extends the provided 'athlete_json' with 'follow' key containing the information about the follow status of
        'athlete_id' with regard to the 'req_id'
        @param athlete_json: dict - Athlete JSON to be extended
        @param follower_id: int - ID of the person who follows the followee
        @param followee_id: int - ID of the person potentially being followed
        """
        follow_rel = AthleteHandler.follow_status(follower_id, followee_id)
        if follow_rel:
            athlete_json['follow'] = {'followed': True, 'opt_out_mode': follow_rel.opt_out_mode}
        else:
            athlete_json['follow'] = None

        return athlete_json


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
    def json_full(athlete: AthleteModel, requesting_id=None):
        athlete_json = athlete.json()
        athlete_roles = AthleteHandler.fetch_roles(athlete.id)
        athlete_json['roles'] = []
        for athlete_role in athlete_roles:
            role = {'id': athlete_role.role_id, 'skill_level': athlete_role.skill_level}
            athlete_json['roles'].append(role)

        # Add list of requesting_id followers
        athlete_followers = AthleteHandler.fetch_followers(athlete.id)
        athlete_json['followers'] = len(athlete_followers)
        # [athlete_json['followers'].append(follower.from_id) for follower in athlete_followers]

        athlete_json = AthleteHandler.add_follower_status(athlete_json, athlete.id, requesting_id)
        # if requesting_id:
        #     follow_rel = AthleteHandler.follow_status(requesting_id, athlete.id)
        #     if follow_rel:
        #         athlete_json['follow'] = {'followed': True, 'opt_out_mode': follow_rel.opt_out_mode}
        #     else:
        #         athlete_json['follow'] = None
        return athlete_json

    @staticmethod
    def log_login(athlete: AthleteModel):
        athlete.last_login = datetime.now().replace(microsecond=0)

    @staticmethod
    def follow(follower_id: int, followee_id: int, data: dict):
        if follower_id == followee_id:
            return {'message': 'the athlete ' + follower_id + ' cannot follow himself!'}, 400
        follower = AthleteHandler.fetch(id=follower_id)
        followee = AthleteHandler.fetch(id=followee_id)
        follow_rel = FollowersModel(follower=follower, followee=followee, opt_out_mode=data['opt_out_mode'])
        session.add(follow_rel)
        try:
            session.commit()
        except e.IntegrityError:
            return {'message': 'Athlete ' + follower_id + ' already follows athlete ' + followee_id}, 400
        return {'follower_id': follower_id, 'followee_id': followee_id}, 200

    @staticmethod
    def update_follow_mode(follower_id: int, followee_id: int, data: dict):
        follow_rel = AthleteHandler.follow_status(follower_id, followee_id)
        if not follow_rel:
            return {'message': 'Athlete ' + follower_id + ' does not follow athlete ' + followee_id}, 400

        follow_rel.opt_out_mode = data['opt_out_mode']
        session.commit()
        return {'message': 'Resource successfully updated'}, 204

    @staticmethod
    def unfollow(follower_id: int, followee_id: int):
        follow_rel = AthleteHandler.follow_status(follower_id, followee_id)
        if not follow_rel:
            return {'message': 'Athlete ' + follower_id + ' does not follow athlete ' + followee_id}, 400

        session.delete(follow_rel)
        session.commit()
        return {'message': 'Resource successfully deleted'}, 204

    @staticmethod
    def search(data: dict):
        athletes = None
        if 'role_id' in data:
            athletes = AthleteModel.query\
                .filter(AthleteModel.name.contains(data['name']), AthleteModel.roles.any(role_id=int(data['role_id'])))\
                .all()
        else:
            athletes = AthleteModel.query\
                .filter(AthleteModel.name.contains(data['name']))\
                .all()
        ret_data = []
        [ret_data.append(AthleteHandler.json_full(a, requesting_id=data['requesting_id'])) for a in athletes]
        return ret_data

    @staticmethod
    def search_followers(data: dict):
        follow_relationships = AthleteHandler.fetch_followers(data['requesting_id'],
                                                              role_id=data['role_id'],
                                                              opt_out_mode=data['opt_out_mode'])
        followers = []
        for relationship in follow_relationships:
            follower_json = relationship.follower.json()
            follower_json['follow'] = {'followed': True, 'opt_out_mode': relationship.opt_out_mode}
            followers.append(follower_json)
        # follower_json = [AthleteHandler.json_full relationship.follower.json()
        return followers


