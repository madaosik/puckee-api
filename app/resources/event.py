from app.core.model import EventHandler, AthleteHandler
from flask_restful import Resource, reqparse
from flask import current_app as app


class Event(Resource):
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
    def get():
        return [EventHandler.json_full(event, att_details=False) for event in EventHandler.fetch_all()]

    @staticmethod
    def post():
        app.logger.info(f'parsed args: {Event.parser.parse_args()}')
        data = Event.parser.parse_args()
        organizer = AthleteHandler.fetch_by_id(data['organizer_id'])
        return EventHandler.add(organizer, data)


class EventByDate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('start_date', type=str, required=True,
                        help='Provide the start date of the requested period in \'start_date\' in format \'YYYY-MM-DD\'')
    parser.add_argument('end_date', type=str, required=True,
                        help='Provide the end date of the requested period in \'end_date\' in format \'YYYY-MM-DD\'')

    @staticmethod
    def get():
        print("cus")
        app.logger.info(f'parsed args: {EventByDate.parser.parse_args()}') #a
        data = EventByDate.parser.parse_args()
        return [EventHandler.json_full(event, att_details=False) for event in EventHandler.fetch_by_date(data)]


class EventUpdater(Event):
    @staticmethod
    def get(event_id: int):
        event = EventHandler.fetch_by_id(event_id)
        return EventHandler.json_full(event, att_details=True)

    @staticmethod
    def delete(event_id: int):
        return EventHandler.delete(event_id)

    @staticmethod
    def put(event_id: int):
        data = Event.parser.parse_args()
        return EventHandler.update(event_id, data)


class EventParticipants(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('athlete_id', type=int, required=True,
                        help='ID of the user attending the event')
    parser.add_argument('athlete_role', type=str, required=True,
                        help='Provide role of the athlete in \'athlete_role\'')

    @staticmethod
    def get(event_id: int):
        return {
            'player': [player.json() for player in EventHandler.players.fetch_all(event_id)],
            'organizer': [organizer.json() for organizer in EventHandler.organizers.fetch_all(event_id)],
            'goalie': [goalie.json() for goalie in EventHandler.goalies.fetch_all(event_id)],
            'referee': [referee.json() for referee in EventHandler.referees.fetch_all(event_id)],
        }

    @staticmethod
    def post(event_id: int):
        app.logger.info(f'parsed args: {EventParticipants.parser.parse_args()}')
        data = EventParticipants.parser.parse_args()
        return EventHandler.add_participant(event_id, data)

    @staticmethod
    def delete(event_id: int):
        app.logger.info(f'parsed args: {EventParticipants.parser.parse_args()}')
        data = EventParticipants.parser.parse_args()
        return EventHandler.delete_participant(event_id, data)


def configure(api):
    api.add_resource(Event, '/api/event')
    api.add_resource(EventByDate, '/api/event/date')
    api.add_resource(EventUpdater, '/api/event/<event_id>')
    api.add_resource(EventParticipants, '/api/event/<event_id>/participants')