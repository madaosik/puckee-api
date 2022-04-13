from app.core.model import GameHandler, AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask_jwt_extended import jwt_required


class GameParticipants(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('athlete_id', type=int, required=True,
                        help='ID of the user attending the event')
    parser.add_argument('athlete_role', type=str, required=True,
                        help='Provide role of the athlete in \'athlete_role\'')

    @staticmethod
    @jwt_required()
    def get(game_id: int):
        return {
            'player': [player.json() for player in GameHandler.players.fetch_all(game_id)],
            # 'organizer': [organizer.json() for organizer in GameHandler.organizers.fetch_all(game_id)],
            'goalie': [goalie.json() for goalie in GameHandler.goalies.fetch_all(game_id)],
            'referee': [referee.json() for referee in GameHandler.referees.fetch_all(game_id)],
        }

    @staticmethod
    # @jwt_required()
    def post(game_id: int):
        app.logger.info(f'parsed args: {GameParticipants.parser.parse_args()}')
        data = GameParticipants.parser.parse_args()
        return GameHandler.add_participant(int(game_id), data)


class GameParticipantsRemoval(Resource):
    @staticmethod
    # @jwt_required()
    def delete(game_id: int, athlete_id: int):
        return GameHandler.delete_participant(int(game_id), int(athlete_id))


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
    api.add_resource(GameParticipantsRemoval, '/api/game/<game_id>/participants/<athlete_id>')
    # api.add_resource(GameOrganizers, '/api/game/<game_id>/organizers/')
    api.add_resource(GameOrganizers, '/api/game/<game_id>/organizers/<athlete_id>')
