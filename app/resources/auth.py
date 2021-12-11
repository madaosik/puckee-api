from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token

from app.core.model import AthleteHandler


class AthleteSignUp(Resource):
    parser = reqparse.RequestParser()
    # parser.add_argument('login', type=str, required=True,
    #                     help='Athlete login')
    parser.add_argument('password', type=str, required=True,
                        help='Athlete password provided in string')
    parser.add_argument('name', type=str, required=True,
                        help='Please provide athlete name')
    parser.add_argument('email', type=str, required=True,
                        help='Please provide athlete email')

    @staticmethod
    def post():
        app.logger.info(f'parsed args: {AthleteSignUp.parser.parse_args()}')
        data = AthleteSignUp.parser.parse_args()
        return AthleteHandler.create(data)


class AthleteLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, required=True,
                        help='Provide athlete\'s email')
    parser.add_argument('password', type=str, required=True,
                        help='Athlete password provided in string')

    @staticmethod
    def post():
        data = AthleteLogin.parser.parse_args()
        app.logger.info(f'parsed args: {data}')
        verified_athlete = AthleteHandler.fetch_verified(data)
        if not verified_athlete:
            return {"message": "Bad username or password"}, 401

        AthleteHandler.log_login(verified_athlete)
        return {
            'access_token': create_access_token(identity=data['email']),
            'athlete': AthleteHandler.json_full(verified_athlete)
        }


def configure(api):
    api.add_resource(AthleteSignUp, '/api/auth/signup')
    api.add_resource(AthleteLogin, '/api/auth/login')
