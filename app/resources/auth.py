from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token

from app.core.model import AthleteHandler

class AthleteSignUpDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True,
                        help='Athlete name provided in name')
    parser.add_argument('name', type=str, required=True,
                        help='Athlete name provided in name')
    parser.add_argument('surname', type=str, required=True,
                        help='Athlete name provided in name')
    parser.add_argument('birth_month', type=str, required=True,
                        help='Please provide athlete email')
    parser.add_argument('roles', type=dict, action='append', required=True,
                        help='Please provide roles and skill dictionary in \'roles\'')

    @staticmethod
    def post():
        data = AthleteSignUpDetails.parser.parse_args()
        app.logger.info(f'parsed args: {data}')
        return AthleteHandler.add_athlete_details(data)


class AthleteSignUp(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password', type=str, required=True,
                        help='Athlete password provided in string')
    parser.add_argument('email', type=str, required=True,
                        help='Please provide athlete email')
    # parser.add_argument('roles', type=int, action='append', required=True,
    #                     help='Please provide roles in \'roles\'!')

    @staticmethod
    def post():
        app.logger.info(f'parsed args: {AthleteSignUp.parser.parse_args()}')
        data = AthleteSignUp.parser.parse_args()
        return AthleteHandler.add(data)


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
            return {"message": "Neznámé uživatelské jméno nebo neplatné heslo!"}, 401

        AthleteHandler.log_login(verified_athlete)
        return {
            'access_token': create_access_token(identity=data['email']),
            'athlete': AthleteHandler.json_full(verified_athlete)
        }


def configure(api):
    api.add_resource(AthleteSignUp, '/api/auth/signup')
    api.add_resource(AthleteLogin, '/api/auth/login')
    api.add_resource(AthleteSignUpDetails, '/api/auth/signup-details')
