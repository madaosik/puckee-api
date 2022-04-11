from app.core.model.models import GameModel, AthleteModel, IceRinkModel, TIME_FORMAT, DATE_FORMAT
from app.core.db_base import session
from sqlalchemy import exc as e
from sqlalchemy import asc
from datetime import datetime, time, date
from enum import Enum

class AttendeeRole(Enum):
    PLAYER = 0
    ORGANIZER = 1
    GOALIE = 2
    REFEREE = 3


class Attendee:
    def __init__(self, role: AttendeeRole):
        self.role = role

    def fetch_all(self, event_id: int):
        if self.role == AttendeeRole.PLAYER:
            attendees = AthleteModel.query.filter(AthleteModel.games_played.any(id=event_id)).all()
        elif self.role == AttendeeRole.ORGANIZER:
            attendees = AthleteModel.query.filter(AthleteModel.games_organized.any(id=event_id)).all()
        elif self.role == AttendeeRole.GOALIE:
            attendees = AthleteModel.query.filter(AthleteModel.games_goalied.any(id=event_id)).all()
        elif self.role == AttendeeRole.REFEREE:
            attendees = AthleteModel.query.filter(AthleteModel.games_refereed.any(id=event_id)).all()
        return attendees

    def add(self, game_id: int, athlete_id: int):
        event = GameHandler.fetch_by_id(game_id)
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        if self.role == AttendeeRole.PLAYER:
            event.players.append(athlete)
        elif self.role == AttendeeRole.ORGANIZER:
            event.organizers.append(athlete)
        elif self.role == AttendeeRole.GOALIE:
            event.goalies.append(athlete)
        elif self.role == AttendeeRole.REFEREE:
            event.referees.append(athlete)
        session.commit()
        return 'SUCCESS', 204

    def delete(self, game_id: int, athlete_id: int):
        event = GameHandler.fetch_by_id(game_id)
        if self.role == AttendeeRole.PLAYER:
            athlete = AthleteModel.query \
                .filter(AthleteModel.games_played.any(id=game_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Athlete with id {} is not attending the event {}'.format(athlete_id, game_id))
            event.players.remove(athlete)
        elif self.role == AttendeeRole.ORGANIZER:
            athlete = AthleteModel.query \
                .filter(AthleteModel.games_organized.any(id=game_id)) \
                .filter_by(id=athlete_id) \
                .first_or_404(description='Organizer with id {} is not organizing the event {}'.format(athlete_id, game_id))
            event.organizers.remove(athlete)
        elif self.role == AttendeeRole.GOALIE:
            athlete = AthleteModel.query \
                .filter(AthleteModel.games_goalied.any(id=game_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Goalie with id {} is not attending the event {}'.format(athlete_id, game_id))
            event.goalies.remove(athlete)
        elif self.role == AttendeeRole.REFEREE:
            athlete = AthleteModel.query \
                .filter(AthleteModel.games_refereed.any(id=game_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Referee with id {} is not attending the event {}'.format(athlete_id, game_id))
            event.referees.remove(athlete)
        session.commit()
        return {'message': 'Resource successfully deleted'}, 204


class GameHandler:
    players = Attendee(AttendeeRole.PLAYER)
    organizers = Attendee(AttendeeRole.ORGANIZER)
    goalies = Attendee(AttendeeRole.GOALIE)
    referees = Attendee(AttendeeRole.REFEREE)

    @staticmethod
    def fetch_page(page_id: int, per_page: int):
        # print(page)
        # print(per_page)
        # cus = GameModel.query.order_by(asc(GameModel.date)).paginate(page, per_page, error_out=False)
        games_page = GameModel.query.order_by(asc(GameModel.date)).paginate(page_id, per_page, error_out=False).items
        next_page_id = None if len(games_page) < per_page else page_id + 1
        prev_page_id = None if page_id == 1 else page_id - 1
        # game_ids = [game.id for game in cus.items]
        # print(game_ids)
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
    def json_full(game: GameModel, att_details=False):
        event_json = game.json()
        organizers = AthleteModel.query\
            .filter(AthleteModel.games_organized.any(id=game.id))\
            .all()
        players = GameHandler.players.fetch_all(game.id)
        goalies = GameHandler.goalies.fetch_all(game.id)
        referees = GameHandler.referees.fetch_all(game.id)

        if att_details:
            event_json['organizers'] = [o.json() for o in organizers]
            event_json['players'] = [o.json() for o in players]
            event_json['goalies'] = [o.json() for o in goalies]
            event_json['referees'] = [o.json() for o in referees]
        else:
            event_json['organizers'] = [o.id for o in organizers]
            event_json['players'] = [o.id for o in players]
            event_json['goalies'] = [o.id for o in goalies]
            event_json['referees'] = [o.id for o in referees]

        return event_json

    @staticmethod
    def add_participant(event_id: int, data: dict):
        role_ind = int(data['athlete_role'])
        if role_ind == 1:
            return GameHandler.players.add(event_id, data['athlete_id'])
        elif role_ind == 2:
            return GameHandler.goalies.add(event_id, data['athlete_id'])
        elif role_ind == 3:
            return GameHandler.referees.add(event_id, data['athlete_id'])
        elif role_ind == 4:
            return GameHandler.organizers.add(event_id, data['athlete_id'])
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404

    @staticmethod
    def delete_participant(event_id: int, data: dict):
        role_ind = int(data['athlete_role'])
        if role_ind == 1:
            return GameHandler.players.delete(event_id, data['athlete_id'])
        elif role_ind == 2:
            return GameHandler.goalies.delete(event_id, data['athlete_id'])
        elif role_ind == 3:
            return GameHandler.referees.delete(event_id, data['athlete_id'])
        elif role_ind == 4:
            return GameHandler.organizers.delete(event_id, data['athlete_id'])
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404
