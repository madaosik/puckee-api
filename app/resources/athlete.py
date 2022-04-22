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
        req_args = request.args
        check_result = check_paging_params(req_args)
        if check_result is not None:
            return check_result
        app.logger.info('parsed GET params: \'page_id\': \'{}\', \'per_page\': \'{}\', \'requesting_id\': \'{}\''
                        .format(req_args['page_id'], req_args['per_page'], req_args['requesting_id']))

        page_id = int(req_args['page_id'])
        athletes_page, next_page_id, prev_page_id = AthleteHandler.fetch_page(page_id, int(req_args['per_page']))
        ret_dict = {'next_id': next_page_id, 'previous_id': prev_page_id, 'data': []}
        for athlete in athletes_page:
            ret_dict['data'].append(AthleteHandler.json_full(athlete, requesting_id=req_args['requesting_id']))
        return ret_dict
        # return [AthleteHandler.json_full(athlete) for athlete in AthleteHandler.fetch_all()]

    @staticmethod
    # @jwt_required()
    def post():
        app.logger.info(f'parsed args: {Athlete.parser.parse_args()}')
        data = Athlete.parser.parse_args()
        return AthleteHandler.add(data)


class AthleteFollowed(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('opt_out_mode', type=bool, required=True,
                        help='Please provide type of the follow relationship (true for opt_out)')

    @staticmethod
    # @jwt_required()
    def post(follower_id: int, followee_id: int):
        data = AthleteFollowed.parser.parse_args()
        app.logger.info('parsed POST params: \'opt_out_mode\': \'{}\''.format(data['opt_out_mode']))
        return AthleteHandler.follow(follower_id, followee_id, data)

    @staticmethod
    # @jwt_required()
    def delete(follower_id: int, followee_id: int):
        return AthleteHandler.unfollow(follower_id, followee_id)

    @staticmethod
    def put(follower_id: int, followee_id: int):
        data = AthleteFollowed.parser.parse_args()
        app.logger.info('parsed PUT params: \'opt_out_mode\': \'{}\''.format(data['opt_out_mode']))
        return AthleteHandler.update_follow_mode(follower_id, followee_id, data)


class AthleteSearch(Resource):
    @staticmethod
    def get():
        """Requires 'name', 'role_id' and 'requesting_id' (to identify the follow relationship) request arguments"""
        data = request.args
        if len(data) < 3:
            return {'message': 'Search parameters have not been provided!'}, 404
        return AthleteHandler.search(data)


def configure(api):
    api.add_resource(Athlete, '/api/athlete')
    api.add_resource(AthleteSearch, '/api/athlete/search')
    api.add_resource(AthleteFollowed, '/api/athlete/<follower_id>/follow/<followee_id>')