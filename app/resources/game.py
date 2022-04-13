from app.core.model import GameHandler, AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required

from app.resources.utils import check_paging_params


class Game(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True,
                        help='Provide name of the event in \'name\'')
    parser.add_argument('organizer_id', type=int, required=True,
                        help='Provide id of the organizer in \'organizer_id\'')
    parser.add_argument('total_places', type=int, required=True,
                        help='Total count of places has to be provided')
    parser.add_argument('start', type=str, required=True,
                        help='Provide start time in \'start\'')
    parser.add_argument('duration', type=str, required=True,
                        help='Provide duration time in \'duration\'')
    parser.add_argument('exp_level', type=int, required=True,
                        help='Provide expected level of game in \'exp_level\'')

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
        games_page, next_page_id, prev_page_id = GameHandler.fetch_page(page_id, int(page_info['per_page']))
        ret_dict = {'next_id': next_page_id, 'previous_id': prev_page_id, 'data': []}
        for game in games_page:
            ret_dict['data'].append(GameHandler.json_full(game, att_details=True))
        return ret_dict

    @staticmethod
    # @jwt_required()
    def post():
        app.logger.info(f'parsed args: {Game.parser.parse_args()}')
        data = Game.parser.parse_args()
        organizer = AthleteHandler.fetch(id=data['organizer_id'])
        return GameHandler.add(organizer, data)


class GameByDate(Resource):
    @staticmethod
    @jwt_required()
    def get():
        dates = request.args
        if 'start_date' not in dates:
            app.logger.error('\'start_date\' has not been provided as GET parameter for /api/event/date')
            return {'message': '\'start_date\' has not been provided as GET parameter for /api/event/date'}, 400
        elif 'end_date' not in dates:
            app.logger.error('\'end_date\' has not been provided as GET parameter for /api/event/date')
            return {'message': '\'end_date\' has not been provided as GET parameter /api/event/date'}, 400
        app.logger.info('parsed GET params: \'start_date\': \'{}\', \'end_date\': \'{}\''
                        .format(dates['start_date'], dates['end_date']))
        try:
            games = GameHandler.fetch_by_date(dates)
        except ValueError as e:
            return {'message': str(e)}, 400
        return [GameHandler.json_full(game, att_details=True) for game in games]


class GameUpdater(Game):
    @staticmethod
    @jwt_required()
    def get(event_id: int):
        event = GameHandler.fetch_by_id(event_id)
        return GameHandler.json_full(event, att_details=True)

    @staticmethod
    @jwt_required()
    def delete(event_id: int):
        return GameHandler.delete(event_id)

    @staticmethod
    @jwt_required()
    def put(event_id: int):
        data = Game.parser.parse_args()
        return GameHandler.update(event_id, data)


def configure(api):
    api.add_resource(Game, '/api/game')
    api.add_resource(GameByDate, '/api/game/date')
    api.add_resource(GameUpdater, '/api/game/<event_id>')
