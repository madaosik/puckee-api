from enum import IntEnum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Float
from sqlalchemy.types import DateTime, Time, Date, Boolean
from flask import jsonify

from werkzeug.security import generate_password_hash
# import uuid
import json
from datetime import datetime, time, date

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
TIME_FORMAT = '%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
GAME_NAME_LEN_LIMIT = 25

sqlDb: SQLAlchemy = SQLAlchemy(session_options={"autoflush": True})

game_organizers = sqlDb.Table('game_organizers',
                              Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                              Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                              )

game_players = sqlDb.Table('game_players',
                           Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                           Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                           )

game_anonym_players = sqlDb.Table('game_anonym_players',
                                  Column('anonym_id', Integer, ForeignKey('athlete_anonymous.id'), primary_key=True),
                                  Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                           )

game_goalies = sqlDb.Table('game_goalies',
                           Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                           Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                           )

game_anonym_goalies = sqlDb.Table('game_anonym_goalies',
                                  Column('anonym_id', Integer, ForeignKey('athlete_anonymous.id'), primary_key=True),
                                  Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                           )

game_referees = sqlDb.Table('game_referees',
                            Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
                            Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                            )

game_anonym_referees = sqlDb.Table('game_anonym_referees',
                                  Column('anonym_id', Integer, ForeignKey('athlete_anonymous.id'), primary_key=True),
                                  Column('game_id', Integer, ForeignKey('game.id'), primary_key=True),
                           )


class GameModel(sqlDb.Model):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(GAME_NAME_LEN_LIMIT), nullable=False)
    exp_players_cnt = Column(Integer, nullable=False)
    exp_goalies_cnt = Column(Integer, nullable=False)
    exp_referees_cnt = Column(Integer, nullable=False)
    # child = sqlDb.relationship("IceRinkModel", back_populates="parent", uselist=False)
    location_id = Column(Integer, ForeignKey('icerink.id'))
    location = sqlDb.relationship("IceRinkModel", back_populates="games")
    # location = sqlDb.relationship("IceRinkModel", back_populates="games")
    # location = sqlDb.relationship("IceRinkModel", backref=sqlDb.backref('athlete', uselist=False))
    est_price = Column(Integer, nullable=False)
    remarks = Column(String(200), nullable=True)
    # date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    other_costs = Column(Integer, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    goalie_renum = Column(Integer, nullable=False)
    referee_renum = Column(Integer, nullable=False)
    players = sqlDb.relationship('AthleteModel', secondary=game_players, lazy='subquery',
                                 backref=sqlDb.backref('games_played', lazy=True))
    anonym_players = sqlDb.relationship('AnonymousAthleteModel', secondary=game_anonym_players, lazy='subquery',
                                        backref=sqlDb.backref('games_anonym_played', lazy=True))
    organizers = sqlDb.relationship('AthleteModel', secondary=game_organizers, lazy='subquery',
                                    backref=sqlDb.backref('games_organized', lazy=True))
    goalies = sqlDb.relationship('AthleteModel', secondary=game_goalies, lazy='subquery',
                                 backref=sqlDb.backref('games_goalied', lazy=True))
    anonym_goalies = sqlDb.relationship('AnonymousAthleteModel', secondary=game_anonym_goalies, lazy='subquery',
                                        backref=sqlDb.backref('games_anonym_goalied', lazy=True))
    referees = sqlDb.relationship('AthleteModel', secondary=game_referees, lazy='subquery',
                                  backref=sqlDb.backref('games_refereed', lazy=True))
    anonym_referees = sqlDb.relationship('AnonymousAthleteModel', secondary=game_anonym_referees, lazy='subquery',
                                         backref=sqlDb.backref('games_anonym_refereed', lazy=True))
    exp_skill = Column(Integer, nullable=False)
    time_created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    last_update = Column(TIMESTAMP, nullable=False, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def json(self):
        creation_time_formatted = self.time_created.isoformat()
        last_update_formatted = self.last_update.isoformat()
        return {"id": self.id,
                "name": self.name,
                "exp_players_cnt": self.exp_players_cnt,
                "exp_goalies_cnt": self.exp_goalies_cnt,
                "exp_referees_cnt": self.exp_referees_cnt,
                "location_id": self.location_id,
                "est_price": self.est_price,
                "remarks": self.remarks,
                # "date":  datetime.strftime(self.date, DATE_FORMAT),
                "start_time": datetime.strftime(self.start_time, DATETIME_FORMAT),
                "end_time": datetime.strftime(self.end_time, DATETIME_FORMAT),
                "other_costs": self.other_costs,
                "is_private": self.is_private,
                "goalie_renum": self.goalie_renum,
                "referee_renum": self.referee_renum,
                "exp_skill": self.exp_skill,
                "creation_time": creation_time_formatted,
                "last_updated": last_update_formatted
                }


# athlete_roles = sqlDb.Table('athlete_roles',
#                             Column('role_id', Integer, ForeignKey('athlete_role.id'), primary_key=True),
#                             Column('athlete_id', Integer, ForeignKey('athlete.id'), primary_key=True),
#                             Column('skill_level', Float),
#                             )
class AnonymousAthleteModel(sqlDb.Model):
    __tablename__ = 'athlete_anonymous'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    added_by = Column(Integer, ForeignKey('athlete.id'), nullable=False)
    added_in = Column(Integer, ForeignKey('game.id'), nullable=False)
    created = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, name, added_by, added_in):
        self.name = name
        self.added_by = added_by
        self.added_in = added_in

    def json(self):
        creation_time_formatted = self.created.isoformat()
        return {"id": self.id,
                "name": self.name,
                "added_by": self.added_by,
                "added_in": self.added_in,
                "creation_time": creation_time_formatted,
                }


class FollowersModel(sqlDb.Model):
    __tablename__ = 'followers'
    from_id = Column(ForeignKey('athlete.id'), primary_key=True)
    to_id = Column(ForeignKey('athlete.id'), primary_key=True)
    opt_out_mode = Column(Boolean)

    # def __init__(self, follower_id: int, followee_id: int, opt_out_mode: bool):
    #     self.from_id = follower_id
    #     self.to_id = followee_id
    #     self.opt_out_mode = opt_out_mode


class AthleteModel(sqlDb.Model):
    __tablename__ = 'athlete'

    id = Column(Integer, primary_key=True, autoincrement=True)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50))
    email = Column(String(50), nullable=False)
    last_login = Column(TIMESTAMP)
    last_modified = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())

    roles = sqlDb.relationship("AthleteRoleAssociationModel", backref=sqlDb.backref('roles_assigned', lazy=True))
    # Inspired by https://stackoverflow.com/questions/25177451/sqlalchemy-self-referential-many-to-many-relationship-with-extra-column
    followed_by = sqlDb.relationship('FollowersModel', backref='follower', primaryjoin=id == FollowersModel.from_id)
    followee = sqlDb.relationship('FollowersModel', backref='followee', primaryjoin=id == FollowersModel.to_id)

    def __init__(self, email, password):
        self.password_hash = generate_password_hash(password, method='sha256')
        # self.name = ""
        self.email = email
        # self.perf_level = perf_level

    def json(self):
        try:
            formatted_last_login = self.last_login.isoformat()
        except AttributeError:
            formatted_last_login = 'null'
        formatted_last_update = self.last_modified.isoformat().strip('"')
        return {"id": self.id,
                "email": self.email,
                "name": self.name,
                # "perf_level": self.perf_level,
                "last_login": formatted_last_login,
                "last_update": formatted_last_update
                }


class IceRinkModel(sqlDb.Model):
    __tablename__ = 'icerink'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    address = Column(String(40))
    price_per_hour = Column(Integer)
    games = sqlDb.relationship("GameModel", back_populates="location")

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "price_per_hour": self.price_per_hour,
        }


class AthleteRoleModel(sqlDb.Model):
    __tablename__ = 'athlete_role'

    id = Column(Integer, primary_key=True)
    role = Column(String(10), nullable=False)
    # players = sqlDb.relationship("AthleteRoleAssociationModel", backref=sqlDb.backref('athletes_in_role', lazy=True))


class AthleteRoleAssociationModel(sqlDb.Model):
    __tablename__ = 'athlete_roles_assoc'
    athlete_id = Column(ForeignKey('athlete.id'), primary_key=True)
    role_id = Column(ForeignKey('athlete_role.id'), primary_key=True)
    skill_level = Column(Float)

    def __init__(self, role_id, skill_level=0):
        self.role_id = role_id
        self.skill_level = skill_level


class AthleteRole(IntEnum):
    USER = 1
    PLAYER = 2
    GOALIE = 3
    REFEREE = 4
    ORGANIZER = 5