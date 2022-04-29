from app.core.model import GameHandler, AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app, request
from flask_jwt_extended import jwt_required


class GameParticipants(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('athlete_id', type=int, required=False,
                        help='ID of the user attending the event')
    parser.add_argument('athlete_name', type=str, required=False,
                        help='ID of the user attending the event')
    parser.add_argument('athlete_role', type=str, required=True,
                        help='Provide role of the athlete in \'athlete_role\'')
    parser.add_argument('requesting_id', type=int, required=False,
                        help='Provide the id of requesting athlete in \'requesting_id\'')

    @staticmethod
    # @jwt_required()
    def get(game_id: int):
        data = request.args
        if 'requesting_id' not in data:
            return {'message': 'Provide \'requesting_id\' parameter!'}, 400
        return {
            'organizers': [AthleteHandler.json_full(o, requesting_id=data['requesting_id']) for o in GameHandler.organizers.fetch_all(game_id)],
            'players': [AthleteHandler.json_full(p, requesting_id=data['requesting_id']) for p in GameHandler.players.fetch_all(game_id)],
            'anonym_players': [p.json() for p in GameHandler.anonym_players.fetch_all(game_id)],
            'goalies': [AthleteHandler.json_full(g, requesting_id=data['requesting_id']) for g in GameHandler.goalies.fetch_all(game_id)],
            'anonym_goalies': [g.json() for g in GameHandler.anonym_goalies.fetch_all(game_id)],
            'referees': [AthleteHandler.json_full(r, requesting_id=data['requesting_id']) for r in GameHandler.referees.fetch_all(game_id)],
            'anonym_referees': [r.json() for r in GameHandler.anonym_referees.fetch_all(game_id)],
        }

    @staticmethod
    # @jwt_required()
    def post(game_id: int):
        data = GameParticipants.parser.parse_args()
        app.logger.info(f'parsed args: {data}')
        if not (data['athlete_id'] or data['athlete_name']):
            return {'message': 'Provide either \'athlete_id\' or \'athlete_name\' parameter!'}, 400

        return GameHandler.add_participant(int(game_id), data)

    @staticmethod
    def delete(game_id: int):
        data = request.args
        if ('athlete_id' in data) or ('athlete_name' in data):
            return GameHandler.delete_participant(int(game_id), data)
        else:
            return {'message': 'Provide either \'athlete_id\' or \'athlete_name\' parameter!'}, 400



# class GameParticipantsRemoval(Resource):
#     @staticmethod
#     # @jwt_required()
#     def delete(game_id: int, athlete_id: int):
#         return GameHandler.delete_participant(int(game_id), int(athlete_id))


class GameOrganizers(Resource):
    @staticmethod
    # @jwt_required()
    def get(game_id: int):
        return {[organizer.json() for organizer in GameHandler.organizers.fetch_all(game_id)]}, 200

    @staticmethod
    # @jwt_required()
    def post(game_id: int, athlete_id: int):
        return GameHandler.add_organizer(int(game_id), int(athlete_id))

    @staticmethod
    # @jwt_required()
    def delete(game_id: int, athlete_id: int):
        return GameHandler.delete_organizer(int(game_id), int(athlete_id))


def configure(api):
    api.add_resource(GameParticipants, '/api/game/<game_id>/participants')
    # api.add_resource(GameParticipantsRemoval, '/api/game/<game_id>/participants/<athlete_id>')
    api.add_resource(GameOrganizers, '/api/game/<game_id>/organizers/<athlete_id>')
