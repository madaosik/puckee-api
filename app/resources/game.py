from app.core.model import GameHandler, AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required

from app.resources.utils import check_paging_params


class Game(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('name', type=str, required=True,
                        help='Provide name of the event in \'name\'')
    parser.add_argument('exp_players_cnt', type=int, required=True,
                        help='Provide the expected count of players in \'exp_players_cnt\'')
    parser.add_argument('exp_goalies_cnt', type=int, required=True,
                        help='Provide the expected count of goalies in \'exp_goalies_cnt\'')
    parser.add_argument('exp_referees_cnt', type=int, required=True,
                        help='Provide the expected count of referees in \'exp_referees_cnt\'')
    parser.add_argument('location_id', type=int, required=True,
                        help='Provide the expected location id in \'location_id\'')
    parser.add_argument('est_price', type=int, required=True,
                        help='Provide the expected price for players in \'est_price\'')
    parser.add_argument('remarks', type=str, required=True,
                        help='Provide remarks in \'remarks\'')
    parser.add_argument('start_time', type=str, required=True,
                        help='Provide start_time in \'start_time\'')
    parser.add_argument('end_time', type=str, required=True,
                        help='Provide end_time in \'end_time\'')
    parser.add_argument('other_costs', type=int, required=True,
                        help='Provide the other_costs in \'other_costs\'')
    parser.add_argument('is_private', type=int, required=False,
                        help='Provide private flag value in \'is_private\'')
    parser.add_argument('goalie_renum', type=int, required=True,
                        help='Provide the goalie_renum in \'goalie_renum\'')
    parser.add_argument('referee_renum', type=int, required=True,
                        help='Provide the referee_renum in \'referee_renum\'')
    parser.add_argument('est_price', type=int, required=True,
                        help='Provide the expected price for players in \'est_price\'')
    parser.add_argument('players', type=int, action='append', required=False,
                        help='Provide the list of signed up player IDs in \'players\'')
    parser.add_argument('organizers', type=int, action='append', required=False,
                        help='Provide the list of signed up organizers IDs in \'organizers\'')
    parser.add_argument('goalies', type=int, action='append', required=False,
                        help='Provide the list of signed up goalies IDs in \'goalies\'')
    parser.add_argument('referees', type=int, action='append', required=False,
                        help='Provide the list of signed up referees IDs in \'referees\'')
    parser.add_argument('anonym_players', type=str, action='append', required=False,
                        help='Provide the list of anonym_players in \'anonym_players\'')
    parser.add_argument('anonym_goalies', type=str, action='append', required=False,
                        help='Provide the list of anonym_goalies in \'anonym_goalies\'')
    parser.add_argument('anonym_referees', type=str, action='append', required=False,
                        help='Provide the list of sanonym_referees in \'anonym_referees\'')
    parser.add_argument('exp_skill', type=int, required=True,
                        help='Provide expected skill of the game in \'exp_skill\'')

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
            ret_dict['data'].append(GameHandler.json_full(game, {}, att_details=True))
        return ret_dict

    @staticmethod
    # @jwt_required()
    def post():
        app.logger.info(f'parsed args: {Game.parser.parse_args()}')
        data = Game.parser.parse_args()
        # organizer = AthleteHandler.fetch(id=data['organizer_id'])
        return GameHandler.add(data)

    @staticmethod
    def put():
        app.logger.info(f'parsed args: {Game.parser.parse_args()}')
        data = Game.parser.parse_args()
        # organizer = AthleteHandler.fetch(id=data['organizer_id'])
        return GameHandler.update(data)


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
    # @jwt_required()
    def get(game_id: int):
        data = request.args
        if 'attendance' not in data:
            app.logger.error('\'attendance\' has not been provided as GET parameter for /api/event/date')
            return {'message': '\'attendance\' has not been provided as GET parameter for /api/event/date'}, 400
        game = GameHandler.fetch_by_id(game_id)
        if data['attendance'] == 'true':
            return GameHandler.json_full(game, data, att_details=True)
        else:
            return game.json(), 200

    @staticmethod
    # @jwt_required()
    def delete(game_id: int):
        return GameHandler.delete(game_id)

    @staticmethod
    # @jwt_required()
    def put(game_id: int):
        data = Game.parser.parse_args()
        return GameHandler.update(game_id, data)


def configure(api):
    api.add_resource(Game, '/api/game')
    api.add_resource(GameByDate, '/api/game/date')
    api.add_resource(GameUpdater, '/api/game/<game_id>')
