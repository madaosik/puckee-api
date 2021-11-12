# from flask.views import MethodView
from flask_restful import Resource
# from flask import jsonify
from app.core.model.models import EventModel
from app.core.model import EventHandler
from flask_restful import Resource, reqparse
from flask import current_app as app


class Event(Resource):
    parser = reqparse.RequestParser()  # only allow changes to the count of places, no name changes allowed
    parser.add_argument('name', type=str, required=True,
                        help='Name of the event')
    parser.add_argument('places', type=int, required=True,
                        help='Total count of places has to be provided')

    @staticmethod
    def get():
        return [event.json() for event in EventHandler.get()]

    @staticmethod
    def post():
        app.logger.info(f'parsed args: {Event.parser.parse_args()}')
        data = Event.parser.parse_args()
        return EventHandler.add(EventModel(data['name'], data['places']))


class EventUpdater(Event):
    @staticmethod
    def get(event_id: int):
        return EventHandler.get_by_id(event_id).json()

    @staticmethod
    def delete(event_id: int):
        return EventHandler.delete(event_id)

    @staticmethod
    def put(event_id: int):
        data = Event.parser.parse_args()
        return EventHandler.update(event_id, data)


def configure(api):
    api.add_resource(Event, '/api/event')
    api.add_resource(EventUpdater, '/api/event/<event_id>')