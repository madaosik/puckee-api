from app.core.model.athlete_handler import AthleteHandler
from app.core.model.attendance_handler import PlayersInGame, GoaliesInGame, RefereesInGame, OrganizersInGame, \
    AthleteRole, AnonymPlayersInGame, AnonymGoaliesInGame, AnonymRefereesInGame
from app.core.model.models import GameModel, AthleteModel, IceRinkModel, TIME_FORMAT, DATE_FORMAT
from app.core.db_base import session
from sqlalchemy import exc as e
from sqlalchemy import asc
from datetime import datetime


class GameHandler:
    organizers = OrganizersInGame()
    players = PlayersInGame()
    anonym_players = AnonymPlayersInGame()
    goalies = GoaliesInGame()
    anonym_goalies = AnonymGoaliesInGame()
    referees = RefereesInGame()
    anonym_referees = AnonymRefereesInGame()

    @staticmethod
    def fetch_page(page_id: int, per_page: int):
        games_page = GameModel.query.order_by(asc(GameModel.date)).paginate(page_id, per_page, error_out=False).items
        next_page_id = None if len(games_page) < per_page else page_id + 1
        prev_page_id = None if page_id == 1 else page_id - 1
        return games_page, next_page_id, prev_page_id

    @staticmethod
    def fetch_by_id(game_id: int):
        return GameModel.query.filter_by(id=game_id)\
            .first_or_404(description='Event with id {} is not available'.format(game_id))

    @staticmethod
    def fetch_by_date(data: dict):
        """
        Returns a list of events in a given timeframe, ordered by datetime
        @param data: A dictionary containing keys 'start_date' and 'end_date'
        @return: List(EventModel)
        """
        try:
            start_timestamp = datetime.strptime(data['start_date'], DATE_FORMAT)
        except ValueError:
            raise ValueError('Unexpected date format for \'start_date\', expected \'YYYY-MM-DD\'')
        try:
            end_timestamp = datetime.strptime(data['end_date'], DATE_FORMAT).replace(hour=23, minute=59)
        except ValueError:
            raise ValueError('Unexpected date format for \'end_date\', expected \'YYYY-MM-DD\'')

        return GameModel.query.filter(GameModel.start <= end_timestamp)\
            .filter(GameModel.start >= start_timestamp)\
            .order_by(asc(GameModel.start))

    @staticmethod
    def add(organizer: AthleteModel, data: dict):
        game = GameModel(name=data['name'],
                         exp_players_cnt=data['exp_players_cnt'],
                         exp_goalies_cnt=data['exp_goalies_cnt'],
                         exp_referees_cnt=data['exp_referees_cnt'],
                         start_time=datetime.strptime(data['start_time'], TIME_FORMAT),
                         end_time=datetime.strptime(data['end_time'], TIME_FORMAT),
                         date=datetime.strptime(data['end_time'], DATE_FORMAT),
                         est_price=data['est_price'],
                         remarks=data['remarks'],
                         other_costs=data['other_costs'],
                         is_private=data['is_private'],
                         goalie_renum=data['goalie_renum'],
                         referee_renum=data['referee_renum'],
                         exp_skill=data['exp_skill'],
                         )
        game.location = IceRinkModel.query.filter_by(id=data['location'])
        game.organizers.append(organizer)
        try:
            session.add(game)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the event."}, 500
        return GameHandler.json_full(game, att_details=True), 201

    @staticmethod
    def delete(game_id: int):
        event = GameHandler.fetch_by_id(game_id)
        session.delete(event)
        session.commit()
        return {'message': 'Event has been deleted'}, 204

    @staticmethod
    def update(game_id: int, data: dict):
        game = GameHandler.fetch_by_id(game_id)
        game.name = data['name']
        game.exp_players_cnt = data['exp_players_cnt']
        game.exp_goalies_cnt = data['exp_goalies_cnt']
        game.exp_referees_cnt = data['exp_referees_cnt']
        game.est_price = data['est_price']
        game.remarks = data['remarks']
        game.date = datetime.strptime(data['start'], DATE_FORMAT)
        game.start_time = datetime.strptime(data['start_time'], TIME_FORMAT)
        game.end_time = datetime.strptime(data['end_time'], TIME_FORMAT)
        game.other_costs = data['other_costs']
        game.is_private = data['is_private']
        game.goalie_renum = data['goalie_renum']
        game.referee_renum = data['referee_renum']
        game.exp_skill = data['exp_skill']
        # handle loc

        session.commit()
        return GameHandler.json_full(game)

    @staticmethod
    def json_full(game: GameModel, req_args: dict, att_details=False):
        req_id = None
        if 'requesting_id' in req_args:
            req_id = req_args['requesting_id']

        game_json = game.json()
        organizers = AthleteModel.query\
            .filter(AthleteModel.games_organized.any(id=game.id))\
            .all()
        players = GameHandler.players.fetch_all(game.id)
        anonym_players = GameHandler.anonym_players.fetch_all(game.id)
        goalies = GameHandler.goalies.fetch_all(game.id)
        anonym_goalies = GameHandler.anonym_goalies.fetch_all(game.id)
        referees = GameHandler.referees.fetch_all(game.id)
        anonym_referees = GameHandler.anonym_referees.fetch_all(game.id)

        if att_details:
            game_json['organizers'] = []
            for o in organizers:
                o_json = o.json()
                o_json = AthleteHandler.add_follow_status(o_json, o.id, req_id)
                game_json['organizers'].append(o_json)

            game_json['players'] = []
            for p in players:
                p_json = p.json()
                p_json = AthleteHandler.add_follow_status(p_json, p.id, req_id)
                game_json['players'].append(p_json)

            game_json['goalies'] = []
            for g in goalies:
                g_json = g.json()
                g_json = AthleteHandler.add_follow_status(g_json, g.id, req_id)
                game_json['goalies'].append(g_json)

            game_json['referees'] = []
            for r in referees:
                r_json = r.json()
                r_json = AthleteHandler.add_follow_status(r_json, r.id, req_id)
                game_json['referees'].append(r_json)

            game_json['anonym_players'] = [o.json() for o in anonym_players]
            game_json['anonym_goalies'] = [o.json() for o in anonym_goalies]
            game_json['anonym_referees'] = [o.json() for o in anonym_referees]
        else:
            game_json['organizers'] = [o.id for o in organizers]
            game_json['players'] = [o.id for o in players]
            game_json['anonym_players'] = [o.id for o in anonym_players]
            game_json['goalies'] = [o.id for o in goalies]
            game_json['anonym_goalies'] = [o.id for o in anonym_goalies]
            game_json['referees'] = [o.id for o in referees]
            game_json['anonym_referees'] = [o.id for o in anonym_referees]

        return game_json

    @staticmethod
    def fetch_participant_role(game: GameModel, athlete_id: int):
        """
        Returns participant's role in a given game (either player OR goalie OR referee)
        @return AthleteRole
        """
        for goalie in game.goalies:
            if goalie.id == athlete_id:
                return AthleteRole.GOALIE
        for referee in game.referees:
            if referee.id == athlete_id:
                return AthleteRole.REFEREE
        for player in game.players:
            if player.id == athlete_id:
                return AthleteRole.PLAYER
        return None

    @staticmethod
    def add_participant(game_id: int, data: dict):
        game = GameHandler.fetch_by_id(game_id)
        role_ind = int(data['athlete_role'])
        if role_ind == AthleteRole.PLAYER:
            return GameHandler.players.add(game, data['athlete_id'])
        elif role_ind == AthleteRole.GOALIE:
            return GameHandler.goalies.add(game, data['athlete_id'])
        elif role_ind == AthleteRole.REFEREE:
            return GameHandler.referees.add(game, data['athlete_id'])
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404

    @staticmethod
    def delete_participant(game_id: int, athlete_id: int):
        game = GameHandler.fetch_by_id(game_id)
        role = GameHandler.fetch_participant_role(game, athlete_id)
        if not role:
            return {'message': "Athlete_id " + str(athlete_id) + "does not participate in " + str(game.id) + "!"}, 404
        if role == AthleteRole.PLAYER:
            return GameHandler.players.delete(game, athlete_id)
        elif role == AthleteRole.GOALIE:
            return GameHandler.goalies.delete(game, athlete_id)
        elif role == AthleteRole.REFEREE:
            return GameHandler.referees.delete(game, athlete_id)

    @staticmethod
    def add_organizer(game_id: int, athlete_id: int):
        game = GameHandler.fetch_by_id(game_id)
        return GameHandler.organizers.add(game, athlete_id)

    @staticmethod
    def delete_organizer(game_id: int, athlete_id: int):
        game = GameHandler.fetch_by_id(game_id)
        return GameHandler.organizers.delete(game, athlete_id)
