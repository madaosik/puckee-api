from app.core.model.models import GameModel, AthleteModel, DATETIME_FORMAT, DURATION_FORMAT, DATESPAN_FORMAT
# from app.core.model import AthleteHandler
from app.core.db_base import session
from sqlalchemy import exc as e
from sqlalchemy import asc
from datetime import datetime
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
            attendees = AthleteModel.query.filter(AthleteModel.events_played.any(id=event_id)).all()
        elif self.role == AttendeeRole.ORGANIZER:
            attendees = AthleteModel.query.filter(AthleteModel.events_organized.any(id=event_id)).all()
        elif self.role == AttendeeRole.GOALIE:
            attendees = AthleteModel.query.filter(AthleteModel.events_goalied.any(id=event_id)).all()
        elif self.role == AttendeeRole.REFEREE:
            attendees = AthleteModel.query.filter(AthleteModel.events_refereed.any(id=event_id)).all()
        return attendees

    def add(self, event_id: int, athlete_id: int):
        event = GameHandler.fetch_by_id(event_id)
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

    def delete(self, event_id: int, athlete_id: int):
        event = GameHandler.fetch_by_id(event_id)
        if self.role == AttendeeRole.PLAYER:
            athlete = AthleteModel.query \
                .filter(AthleteModel.events_played.any(id=event_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Athlete with id {} is not attending the event {}'.format(athlete_id, event_id))
            event.players.remove(athlete)
        elif self.role == AttendeeRole.ORGANIZER:
            athlete = AthleteModel.query \
                .filter(AthleteModel.events_organized.any(id=event_id)) \
                .filter_by(id=athlete_id) \
                .first_or_404(description='Organizer with id {} is not organizing the event {}'.format(athlete_id, event_id))
            event.organizers.remove(athlete)
        elif self.role == AttendeeRole.GOALIE:
            athlete = AthleteModel.query \
                .filter(AthleteModel.events_goalied.any(id=event_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Goalie with id {} is not attending the event {}'.format(athlete_id, event_id))
            event.goalies.remove(athlete)
        elif self.role == AttendeeRole.REFEREE:
            athlete = AthleteModel.query \
                .filter(AthleteModel.events_refereed.any(id=event_id)).filter_by(id=athlete_id) \
                .first_or_404(description='Referee with id {} is not attending the event {}'.format(athlete_id, event_id))
            event.referees.remove(athlete)
        session.commit()
        return {'message': 'Resource successfully deleted'}, 204


class GameHandler:
    players = Attendee(AttendeeRole.PLAYER)
    organizers = Attendee(AttendeeRole.ORGANIZER)
    goalies = Attendee(AttendeeRole.GOALIE)
    referees = Attendee(AttendeeRole.REFEREE)

    @staticmethod
    def fetch_all():
        return GameModel.query.order_by(asc(GameModel.start)).all()

    @staticmethod
    def fetch_by_id(event_id: int):
        return GameModel.query.filter_by(id=event_id)\
            .first_or_404(description='Event with id {} is not available'.format(event_id))

    @staticmethod
    def fetch_by_date(data: dict):
        """
        Returns a list of events in a given timeframe, ordered by datetime
        @param data: A dictionary containing keys 'start_date' and 'end_date'
        @return: List(EventModel)
        """
        try:
            start_timestamp = datetime.strptime(data['start_date'], DATESPAN_FORMAT)
        except ValueError:
            raise ValueError('Unexpected date format for \'start_date\', expected \'YYYY-MM-DD\'')
        try:
            end_timestamp = datetime.strptime(data['end_date'], DATESPAN_FORMAT).replace(hour=23, minute=59)
        except ValueError:
            raise ValueError('Unexpected date format for \'end_date\', expected \'YYYY-MM-DD\'')

        return GameModel.query.filter(GameModel.start <= end_timestamp)\
            .filter(GameModel.start >= start_timestamp)\
            .order_by(asc(GameModel.start))

    @staticmethod
    def add(organizer: AthleteModel, data: dict):
        event = GameModel(name=data['name'], organizer_id=data['organizer_id'],
                          total_places=data['total_places'],
                          start=datetime.strptime(data['start'], DATETIME_FORMAT),
                          duration=datetime.strptime(data['duration'], DURATION_FORMAT))

        event.organizers.append(organizer)
        try:
            session.add(event)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the event."}, 500
        return GameHandler.json_full(event, att_details=True), 201

    @staticmethod
    def delete(event_id: int):
        event = GameHandler.fetch_by_id(event_id)
        session.delete(event)
        session.commit()
        return {'message': 'Event has been deleted'}, 204

    @staticmethod
    def update(event_id: int, data: dict):
        event = GameHandler.fetch_by_id(event_id)
        event.name = data['name']
        event.total_places = data['total_places']
        event.start = datetime.strptime(data['start'], DATETIME_FORMAT)
        event.duration = datetime.strptime(data['duration'], DURATION_FORMAT)
        session.commit()
        return GameHandler.json_full(event)

    @staticmethod
    def json_full(event: GameModel, att_details=False):
        event_json = event.json()
        organizers = AthleteModel.query\
            .filter(AthleteModel.events_organized.any(id=event.id))\
            .all()
        players = GameHandler.players.fetch_all(event.id)
        goalies = GameHandler.goalies.fetch_all(event.id)
        referees = GameHandler.referees.fetch_all(event.id)

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
