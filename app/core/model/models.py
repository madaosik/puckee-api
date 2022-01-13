from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.types import DateTime, Time
from flask import jsonify

from werkzeug.security import generate_password_hash
# import uuid
import json
from datetime import datetime, time

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DURATION_FORMAT = '%H:%M:%S'
DATESPAN_FORMAT = '%Y-%m-%d'
EVENT_NAME_LEN_LIMIT = 25

sqlDb: SQLAlchemy = SQLAlchemy(session_options={"autoflush": True})

event_players = sqlDb.Table('event_players',
                              Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                              Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
                              )

event_organizers = sqlDb.Table('event_organizers',
                               Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                               Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
                               )

event_goalies = sqlDb.Table('event_goalies',
                            Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                            Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
                            )

event_referees = sqlDb.Table('event_referees',
                            Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                            Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
                            )


class GameModel(sqlDb.Model):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(EVENT_NAME_LEN_LIMIT))
    total_places = Column(Integer)
    location = Column(String(40))
    start = Column(DateTime)
    duration = Column(Time)
    players = sqlDb.relationship('AthleteModel', secondary=event_players, lazy='subquery',
                                 backref=sqlDb.backref('events_played', lazy=True))
    organizers = sqlDb.relationship('AthleteModel', secondary=event_organizers, lazy='subquery',
                                    backref=sqlDb.backref('events_organized', lazy=True))
    goalies = sqlDb.relationship('AthleteModel', secondary=event_goalies, lazy='subquery',
                                 backref=sqlDb.backref('events_goalied', lazy=True))
    referees = sqlDb.relationship('AthleteModel', secondary=event_referees, lazy='subquery',
                                  backref=sqlDb.backref('events_refereed', lazy=True))
    exp_level = Column(Integer)
    time_created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    last_update = Column(TIMESTAMP, nullable=False, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def json(self):
        creation_time_formatted = self.time_created.isoformat()
        last_update_formatted = self.last_update.isoformat()
        return {"id": self.id,
                "name": self.name,
                "total_places": self.total_places,
                "location": self.location,
                "start": datetime.strftime(self.start, DATETIME_FORMAT),
                "duration": time.strftime(self.duration, DURATION_FORMAT),
                "exp_level": self.exp_level,
                "creation_time": creation_time_formatted,
                "last_updated": last_update_formatted
                }


athlete_roles = sqlDb.Table('athlete_roles',
                            Column('role_id', Integer, ForeignKey('athlete_role.id'), primary_key=True),
                            Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                            )


class AthleteModel(sqlDb.Model):
    __tablename__ = 'athlete'

    id = Column(Integer, primary_key=True, autoincrement=True)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    roles = sqlDb.relationship('AthleteRoleModel', secondary=athlete_roles, lazy='subquery',
                               backref=sqlDb.backref('roles_assigned', lazy=True))
    perf_level = Column(Integer)
    last_login = Column(TIMESTAMP)
    last_modified = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, email, password, name, perf_level):
        self.password_hash = generate_password_hash(password, method='sha256')
        self.name = name
        self.email = email
        self.perf_level = perf_level

    def json(self):
        try:
            formatted_last_login = self.last_login.isoformat()
        except AttributeError:
            formatted_last_login = 'null'
        formatted_last_update = self.last_modified.isoformat().strip('"')
        return {"id": self.id,
                "email": self.email,
                "name": self.name,
                "perf_level": self.perf_level,
                "last_login": formatted_last_login,
                "last_update": formatted_last_update
                }


class AthleteRoleModel(sqlDb.Model):
    __tablename__ = 'athlete_role'

    id = Column(Integer, primary_key=True)
    role = Column(String(10), nullable=False)
