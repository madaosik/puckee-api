from app.core.model.models import EventModel
from app.core.db_base import session
from sqlalchemy import exc as e


class EventHandler:
    @staticmethod
    def get():
        return EventModel.query.all()

    @staticmethod
    def get_by_id(event_id):
        return EventModel.query.filter_by(event_id=event_id)\
                .first_or_404(description='Event with id={} is not available'.format(event_id))

    @staticmethod
    def add(event):
        try:
            session.add(event)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the event."}, 500
        return event.json(), 201

    @staticmethod
    def delete(event_id: int):
        event = EventHandler.get_by_id(event_id)
        if event:
            session.delete(event)
            session.commit()
            return {'message': 'Event has been deleted'}

    @staticmethod
    def update(event_id: int, data: dict):
        event = EventHandler.get_by_id(event_id)
        if event:
            event.name = data['name']
            event.places = data['places']
            session.commit()
            return event.json()

