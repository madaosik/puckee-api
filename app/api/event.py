# from flask.views import MethodView
from flask_restful import Resource
# from flask import jsonify
from app.core.model import Event


class EventsApi(Resource):
    @staticmethod
    def get():
        return [event.to_dict() for event in Event.get_events()]


class EventApi(Resource):
    @staticmethod
    def get(event_id: int):
        return Event.get_event(event_id)

def configure(api):
    api.add_resource(EventsApi, '/')
    api.add_resource(EventApi, '/event/<event_id>')