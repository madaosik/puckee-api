from app.core.model.models import AthleteModel
from app.core.model import AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required

from app.resources.utils import check_paging_params


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
    # @jwt_required()
    def get():
        page_info = request.args
        check_result = check_paging_params(page_info)
        if check_result is not None:
            return check_result
        app.logger.info('parsed GET params: \'page_id\': \'{}\', \'per_page\': \'{}\''
                        .format(page_info['page_id'], page_info['per_page']))

        page_id = int(page_info['page_id'])
        athletes_page, next_page_id, prev_page_id = AthleteHandler.fetch_page(page_id, int(page_info['per_page']))
        ret_dict = {'next_id': next_page_id, 'previous_id': prev_page_id, 'data': []}
        for athlete in athletes_page:
            ret_dict['data'].append(AthleteHandler.json_full(athlete))
        return ret_dict
        # return [AthleteHandler.json_full(athlete) for athlete in AthleteHandler.fetch_all()]

    @staticmethod
    # @jwt_required()
    def post():
        app.logger.info(f'parsed args: {Athlete.parser.parse_args()}')
        data = Athlete.parser.parse_args()
        return AthleteHandler.add(data)


def configure(api):
    api.add_resource(Athlete, '/api/athlete')
    #api.add_resource(AthleteUpdater, '/api/athlete/<athlete_id>')