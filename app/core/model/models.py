from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.types import DateTime
from flask import jsonify

from werkzeug.security import generate_password_hash
import json
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DURATION_FORMAT = '%H:%M:%S'

sqlDb: SQLAlchemy = SQLAlchemy(session_options={"autoflush": True})

event_attendees = sqlDb.Table('event_attendees',
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


class EventModel(sqlDb.Model):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    total_places = Column(Integer)
    start = Column(DateTime)
    duration = Column(DateTime)
    players = sqlDb.relationship('AthleteModel', secondary=event_attendees, lazy='subquery',
                                 backref=sqlDb.backref('events_attended', lazy=True))
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
        return {"id": self.id,
                "name": self.name,
                "total_places": self.total_places,
                "start": datetime.strftime(self.start, DATETIME_FORMAT),
                "duration": datetime.strftime(self.duration, DURATION_FORMAT),
                "exp_level": self.exp_level,
                "creation_time": json.dumps(self.time_created, indent=4, sort_keys=True, default=str),
                "last_updated": json.dumps(self.last_update, indent=4, sort_keys=True, default=str)
                }


athlete_roles = sqlDb.Table('athlete_roles',
                            Column('role_id', Integer, ForeignKey('athlete_role.id'), primary_key=True),
                            Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                            )


class AthleteModel(sqlDb.Model):
    __tablename__ = 'athlete'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(30), nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    role = sqlDb.relationship('AthleteRoleModel', secondary=athlete_roles, lazy='subquery',
                              backref=sqlDb.backref('athlete', lazy=True))
    #perf_level = Column(Integer)
    last_login = Column(TIMESTAMP)
    last_modified = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, login, password, name, email):
        self.login = login
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.email = email

    def json(self):
        return {"id": self.id,
                "login": self.login,
                "name": self.name,
                "email": self.email,
                "last_login": json.dumps(self.last_login, indent=4, sort_keys=True, default=str),
                "last_update": json.dumps(self.last_modified, indent=4, sort_keys=True, default=str)
                }


class AthleteRoleModel(sqlDb.Model):
    __tablename__ = 'athlete_role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(10), nullable=False)
    # athlete_id = Column(Integer, ForeignKey('athlete.id', nullable=False))
