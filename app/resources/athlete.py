from app.core.model.models import AthleteModel
from app.core.model import AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required


class Athlete(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('email', type=str, required=True,
                        help='Please provide athlete email')
    parser.add_argument('password', type=str, required=True,
                        help='Athlete password provided in string')
    parser.add_argument('name', type=str, required=True,
                        help='Please provide athlete name')
    parser.add_argument('roles', type=int, action='append', help='Player roles are required', required=True)
    parser.add_argument('perf_level', type=int, required=True, help='Player performance level is expected')

    @staticmethod
    @jwt_required()
    def get():
        return [AthleteHandler.json_full(athlete) for athlete in AthleteHandler.fetch_all()]

    @staticmethod
    @jwt_required()
    def post():
        app.logger.info(f'parsed args: {Athlete.parser.parse_args()}')
        data = Athlete.parser.parse_args()
        return AthleteHandler.add(data)


def configure(api):
    api.add_resource(Athlete, '/api/athlete')
    #api.add_resource(AthleteUpdater, '/api/athlete/<athlete_id>')