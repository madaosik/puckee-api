from app.core.model.models import EventModel, AthleteModel, DATETIME_FORMAT, DURATION_FORMAT
# from app.core.model import AthleteHandler
from app.core.db_base import session
from sqlalchemy import exc as e
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
        event = EventHandler.fetch_by_id(event_id)
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
        event = EventHandler.fetch_by_id(event_id)
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


class EventHandler:
    players = Attendee(AttendeeRole.PLAYER)
    organizers = Attendee(AttendeeRole.ORGANIZER)
    goalies = Attendee(AttendeeRole.GOALIE)
    referees = Attendee(AttendeeRole.REFEREE)

    @staticmethod
    def fetch_all():
        return EventModel.query.all()

    @staticmethod
    def fetch_by_id(event_id: int):
        return EventModel.query.filter_by(id=event_id)\
            .first_or_404(description='Event with id {} is not available'.format(event_id))

    @staticmethod
    def add(organizer: AthleteModel, data: dict):
        event = EventModel(name=data['name'], organizer_id=data['organizer_id'],
                           total_places=data['total_places'],
                           start=datetime.strptime(data['start'], DATETIME_FORMAT),
                           duration=datetime.strptime(data['duration'], DURATION_FORMAT))

        event.organizers.append(organizer)
        try:
            session.add(event)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the event."}, 500
        return EventHandler.json_full(event, att_details=True), 201

    @staticmethod
    def delete(event_id: int):
        event = EventHandler.fetch_by_id(event_id)
        session.delete(event)
        session.commit()
        return {'message': 'Event has been deleted'}, 204

    @staticmethod
    def update(event_id: int, data: dict):
        event = EventHandler.fetch_by_id(event_id)
        event.name = data['name']
        event.total_places = data['total_places']
        event.start = datetime.strptime(data['start'], DATETIME_FORMAT)
        event.duration = datetime.strptime(data['duration'], DURATION_FORMAT)
        session.commit()
        return EventHandler.json_full(event)

    @staticmethod
    def json_full(event: EventModel, att_details=False):
        event_json = event.json()
        organizers = AthleteModel.query\
            .filter(AthleteModel.events_organized.any(id=event.id))\
            .all()
        players = EventHandler.players.fetch_all(event.id)
        goalies = EventHandler.goalies.fetch_all(event.id)
        referees = EventHandler.referees.fetch_all(event.id)

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
        if data['athlete_role'] == 'player':
            return EventHandler.players.add(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'organizer':
            return EventHandler.organizers.add(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'goalie':
            return EventHandler.goalies.add(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'referee':
            return EventHandler.referees.add(event_id, data['athlete_id'])
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404

    @staticmethod
    def delete_participant(event_id: int, data: dict):
        if data['athlete_role'] == 'player':
            return EventHandler.players.delete(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'organizer':
            return EventHandler.organizers.delete(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'goalie':
            return EventHandler.goalies.delete(event_id, data['athlete_id'])
        elif data['athlete_role'] == 'referee':
            return EventHandler.referees.delete(event_id, data['athlete_id'])
        else:
            return 'Unknown athlete role has been provided: \'{}\''.format(data['athlete_role']), 404
