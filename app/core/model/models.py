from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, TIMESTAMP, func

sqlDb: SQLAlchemy = SQLAlchemy(session_options={"autoflush": True})


# class SerializerMixin:
#     def to_dict(self):
#         model_dict = self.__dict__
#         del model_dict['_sa_instance_state']
#         return model_dict


class EventModel(sqlDb.Model):#, SerializerMixin):
    __tablename__ = 'events'

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    places = Column(Integer)
    time_created = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __init__(self, name, places):
        self.name = name
        self.places = places

    def json(self):
        return {"id": self.event_id, "name": self.name, "places": self.places}
