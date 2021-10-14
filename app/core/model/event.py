from app.core.model.models import EventRecord

class Event:
    @staticmethod
    def get_events():
        return EventRecord.query.all()

    @staticmethod
    def get_event(event_id):
        return EventRecord.query.filter_by(event_id=event_id)\
                .first_or_404(description='Event with id={} is not available'.format(event_id))
