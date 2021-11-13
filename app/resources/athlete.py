from app.core.model.models import AthleteModel
from app.core.model import AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app


class Athlete(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('login', type=str, required=True,
                        help='Athlete login')
    parser.add_argument('password', type=str, required=True,
                        help='Athlete password provided in string')
    parser.add_argument('name', type=str, required=True,
                        help='Please provide athlete name')
    parser.add_argument('email', type=str, required=True,
                        help='Please provide athlete email')

    @staticmethod
    def get():
        return [athlete.json() for athlete in AthleteHandler.fetch_all()]

    @staticmethod
    def post():
        app.logger.info(f'parsed args: {Athlete.parser.parse_args()}')
        data = Athlete.parser.parse_args()
        athlete = AthleteModel(data['login'], data['password'], data['name'], data['email'])
        return AthleteHandler.add(athlete)


def configure(api):
    api.add_resource(Athlete, '/api/athlete')
    #api.add_resource(AthleteUpdater, '/api/athlete/<athlete_id>')