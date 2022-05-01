from app.core.model.athlete_handler import AthleteHandler
from app.core.model.icerink_handler import IceRinkHandler

from app.core.model.attendance_handler import PlayersInGame, GoaliesInGame, RefereesInGame, OrganizersInGame, \
    AthleteRole, AnonymPlayersInGame, AnonymGoaliesInGame, AnonymRefereesInGame
from app.core.model.models import GameModel, AthleteModel, IceRinkModel, TIME_FORMAT, DATE_FORMAT, \
    AnonymousAthleteModel, DATETIME_FORMAT, FollowersModel
from app.core.db_base import session
from sqlalchemy import exc as e
from sqlalchemy import asc, or_, and_, not_
from datetime import datetime, time, date


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
        games_page = GameModel.query.order_by(asc(GameModel.start_time)).paginate(page_id, per_page,
                                                                                  error_out=False).items
        next_page_id = None if len(games_page) < per_page else page_id + 1
        prev_page_id = None if page_id == 1 else page_id - 1
        return games_page, next_page_id, prev_page_id

    @staticmethod
    def fetch_by_id(game_id: int):
        return GameModel.query.filter_by(id=game_id) \
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

        return GameModel.query.filter(GameModel.start <= end_timestamp) \
            .filter(GameModel.start >= start_timestamp) \
            .order_by(asc(GameModel.start))

    @staticmethod
    def fetch_by_attendee_id(athlete_id: int, game_limit=None):
        # TODO Optimize the db search by searching only for relevant roles
        if game_limit:
            games = GameModel.query.filter(or_(GameModel.players.any(id=athlete_id),
                                               GameModel.goalies.any(id=athlete_id),
                                               GameModel.referees.any(id=athlete_id))) \
                .order_by(asc(GameModel.start_time)).limit(game_limit).all()
        else:
            games = GameModel.query.filter(or_(GameModel.players.any(id=athlete_id),
                                               GameModel.goalies.any(id=athlete_id),
                                               GameModel.referees.any(id=athlete_id))) \
                .order_by(asc(GameModel.start_time)).all()
        return [GameHandler.json_full(g, {}, att_details=True) for g in games]

    @staticmethod
    def fetch_followee_games(athlete_id: int, game_limit=None):
        """
        Inspired by https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers
        """
        record_lim = 5
        if game_limit:
            record_lim = game_limit

        followed_games = GameModel.query.join(FollowersModel,
                            and_(or_(GameModel.organizers.any(id=FollowersModel.to_id),
                                     GameModel.players.any(id=FollowersModel.to_id),
                                     GameModel.goalies.any(id=FollowersModel.to_id),
                                     GameModel.referees.any(id=FollowersModel.to_id)),
                                 and_(not_(GameModel.organizers.any(id=athlete_id)),
                                      not_(GameModel.players.any(id=athlete_id)),
                                      not_(GameModel.goalies.any(id=athlete_id)),
                                      not_(GameModel.referees.any(id=athlete_id)))
                                 )
                          ).filter(FollowersModel.from_id == athlete_id)\
                            .order_by(asc(GameModel.start_time)).limit(record_lim).all()

        followed_games.sort(key=lambda x:
                            sum([AthleteHandler.follow_status(athlete_id, p.id) is not None for p in x.organizers]) +
                            sum([AthleteHandler.follow_status(athlete_id, p.id) is not None for p in x.players]) +
                            sum([AthleteHandler.follow_status(athlete_id, p.id) is not None for p in x.goalies]) +
                            sum([AthleteHandler.follow_status(athlete_id, p.id) is not None for p in x.referees]),
                            reverse=True
                            )
        print(len(followed_games))
        return [GameHandler.json_full(g, {'requesting_id': athlete_id}, att_details=True) for g in followed_games]

    @staticmethod
    def add(data: dict):
        # try:
        game = GameModel(name=data['name'],
                         exp_players_cnt=data['exp_players_cnt'],
                         exp_goalies_cnt=data['exp_goalies_cnt'],
                         exp_referees_cnt=data['exp_referees_cnt'],
                         start_time=datetime.strptime(data['start_time'], DATETIME_FORMAT),
                         end_time=datetime.strptime(data['end_time'], DATETIME_FORMAT),
                         est_price=data['est_price'],
                         remarks=data['remarks'],
                         other_costs=data['other_costs'],
                         is_private=data['is_private'],
                         goalie_renum=data['goalie_renum'],
                         referee_renum=data['referee_renum'],
                         exp_skill=data['exp_skill'],
                         )
        game.location = IceRinkHandler.fetch(id=data['location_id'])

        try:
            session.add(game)
            session.flush()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the event."}, 500

        [game.organizers.append(AthleteHandler.fetch(id=pid)) for pid in data['organizers']]
        if data['players']:
            [game.players.append(AthleteHandler.fetch(id=pid)) for pid in data['players']]
        if data['goalies']:
            [game.goalies.append(AthleteHandler.fetch(id=pid)) for pid in data['goalies']]
        if data['referees']:
            [game.referees.append(AthleteHandler.fetch(id=pid)) for pid in data['referees']]

        if data['anonym_players']:
            for anonym_player in data['anonym_players']:
                if AthleteHandler.fetch_anonymous(anonym_player):
                    continue
                new_anonym_player = AnonymousAthleteModel(anonym_player, data['organizers'][0], game.id)
                game.anonym_players.append(new_anonym_player)

        if data['anonym_goalies']:
            for anonym_goalie in data['anonym_goalies']:
                if AthleteHandler.fetch_anonymous(anonym_goalie):
                    continue
                new_anonym_goalie = AnonymousAthleteModel(anonym_goalie, data['organizers'][0], game.id)
                game.anonym_players.append(new_anonym_goalie)

        if data['anonym_referees']:
            for anonym_referee in data['anonym_referees']:
                if AthleteHandler.fetch_anonymous(anonym_referee):
                    continue
                new_anonym_referee = AnonymousAthleteModel(anonym_referee, data['organizers'][0], game.id)
                game.anonym_players.append(new_anonym_referee)

        session.commit()
        return GameHandler.json_full(game, {'requesting_id': data['organizers'][0]}, att_details=True), 201

    @staticmethod
    def delete(game_id: int):
        event = GameHandler.fetch_by_id(game_id)
        session.delete(event)
        session.commit()
        return {'message': 'Event has been deleted'}, 204

    @staticmethod
    def update(data: dict):
        game = GameHandler.fetch_by_id(data['id'])
        game.name = data['name']
        game.exp_players_cnt = data['exp_players_cnt']
        game.exp_goalies_cnt = data['exp_goalies_cnt']
        game.exp_referees_cnt = data['exp_referees_cnt']
        game.est_price = data['est_price']
        game.remarks = data['remarks']
        # game.date = datetime.strptime(data['date'], DATE_FORMAT)
        game.start_time = datetime.strptime(data['start_time'], DATETIME_FORMAT)
        game.end_time = datetime.strptime(data['end_time'], DATETIME_FORMAT)
        game.other_costs = data['other_costs']
        game.is_private = data['is_private']
        game.goalie_renum = data['goalie_renum']
        game.referee_renum = data['referee_renum']
        game.exp_skill = data['exp_skill']

        new_location_id = data['location_id']
        if new_location_id != game.location_id:
            game.location = IceRinkHandler.fetch(id=data['location_id'])
        try:
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred updating the event."}, 500
        return GameHandler.json_full(game, {})

    @staticmethod
    def json_full(game: GameModel, req_args: dict, att_details=False):
        req_id = None
        if 'requesting_id' in req_args:
            req_id = req_args['requesting_id']

        game_json = game.json()
        organizers = AthleteModel.query \
            .filter(AthleteModel.games_organized.any(id=game.id)) \
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
                if req_id is not None:
                    o_json = AthleteHandler.add_follower_status(o_json, req_id, o.id)
                game_json['organizers'].append(o_json)

            game_json['players'] = []
            for p in players:
                p_json = p.json()
                if req_id is not None:
                    p_json = AthleteHandler.add_follower_status(p_json, req_id, p.id)
                game_json['players'].append(p_json)

            game_json['goalies'] = []
            for g in goalies:
                g_json = g.json()
                if req_id is not None:
                    g_json = AthleteHandler.add_follower_status(g_json, req_id, g.id)
                game_json['goalies'].append(g_json)

            game_json['referees'] = []
            for r in referees:
                r_json = r.json()
                if req_id is not None:
                    r_json = AthleteHandler.add_follower_status(r_json, req_id, r.id)
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
    def fetch_participant_role(game: GameModel, data: dict):
        """
        Returns participant's role in a given game (either player OR goalie OR referee)
        @return AthleteRole
        """
        if 'athlete_id' in data:
            id = int(data['athlete_id'])
            for goalie in game.goalies:
                if goalie.id == id:
                    return AthleteRole.GOALIE
            for referee in game.referees:
                if referee.id == id:
                    return AthleteRole.REFEREE
            for player in game.players:
                if player.id == id:
                    return AthleteRole.PLAYER
            return None
        else:
            for goalie in game.anonym_goalies:
                if goalie.name == data['athlete_name']:
                    return AthleteRole.GOALIE
            for referee in game.anonym_referees:
                if referee.name == data['athlete_name']:
                    return AthleteRole.REFEREE
            for player in game.anonym_players:
                if player.name == data['athlete_name']:
                    return AthleteRole.PLAYER
            return None

    @staticmethod
    def add_participant(game_id: int, data: dict):
        game = GameHandler.fetch_by_id(game_id)
        role_ind = int(data['athlete_role'])
        if role_ind == AthleteRole.PLAYER:
            if data['athlete_id']:
                return GameHandler.players.add(game, data['athlete_id'])
            else:
                return GameHandler.anonym_players.add(game, data)
        elif role_ind == AthleteRole.GOALIE:
            if data['athlete_id']:
                return GameHandler.goalies.add(game, data['athlete_id'])
            else:
                return GameHandler.anonym_goalies.add(game, data)
        elif role_ind == AthleteRole.REFEREE:
            if data['athlete_id']:
                return GameHandler.referees.add(game, data['athlete_id'])
            else:
                return GameHandler.anonym_referees.add(game, data)
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404

    @staticmethod
    def delete_participant(game_id: int, data: dict):
        game = GameHandler.fetch_by_id(game_id)
        role = GameHandler.fetch_participant_role(game, data)
        if not role:
            if 'athlete_id' in data:
                return {'message': "Athlete '" + data['athlete_id'] + "' does not participate in " + str(
                    game.id) + "!"}, 404
            else:
                return {'message': "Athlete '" + data['athlete_name'] + "' does not participate in " + str(
                    game.id) + "!"}, 404

        if role == AthleteRole.PLAYER:
            if 'athlete_id' in data:
                return GameHandler.players.delete(game, data['athlete_id'])
            else:
                return GameHandler.anonym_players.delete(game, data['athlete_name'])
        elif role == AthleteRole.GOALIE:
            if 'athlete_id' in data:
                return GameHandler.goalies.delete(game, data['athlete_id'])
            else:
                return GameHandler.anonym_goalies.delete(game, data['athlete_name'])
        elif role == AthleteRole.REFEREE:
            if 'athlete_id' in data:
                return GameHandler.referees.delete(game, data['athlete_id'])
            else:
                return GameHandler.anonym_referees.delete(game, data['athlete_name'])

    @staticmethod
    def add_organizer(game_id: int, athlete_id: int):
        game = GameHandler.fetch_by_id(game_id)
        return GameHandler.organizers.add(game, athlete_id)

    @staticmethod
    def delete_organizer(game_id: int, athlete_id: int):
        game = GameHandler.fetch_by_id(game_id)
        return GameHandler.organizers.delete(game, athlete_id)
