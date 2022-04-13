from enum import IntEnum

from app.core.model.models import AthleteModel, GameModel
from app.core.db_base import session


class AthleteRole(IntEnum):
    USER = 1
    PLAYER = 2
    GOALIE = 3
    REFEREE = 4
    ORGANIZER = 5


class PlayersInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AthleteModel.query.filter(AthleteModel.games_played.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        if len(game.players) < game.exp_players_cnt:
            game.players.append(athlete)
            session.commit()
            return {'game_id': game.id, 'athlete_id': athlete.id, 'role_id': AthleteRole.PLAYER}, 200
        else:
            return {'message': 'Could not add the player to the game as it is already full ' + str(game.exp_players_cnt)}, 404

    @staticmethod
    def delete(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query \
            .filter(AthleteModel.games_played.any(id=game.id)).filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id {} is not playing the event {}'.format(athlete_id, game.id))
        game.players.remove(athlete)
        session.commit()
        return {'message': 'Player successfully removed from game ' + str(game.id)}, 204


class GoaliesInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AthleteModel.query.filter(AthleteModel.games_goalied.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        if len(game.goalies) < game.exp_goalies_cnt:
            game.goalies.append(athlete)
            session.commit()
            return {'game_id': game.id, 'athlete_id': athlete.id, 'role_id': AthleteRole.GOALIE}, 200
        else:
            return {'message': 'Could not add the goalie to the game as it is already full ' + str(
                game.exp_goalies_cnt)}, 404

    @staticmethod
    def delete(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query \
            .filter(AthleteModel.games_goalied.any(id=game.id)).filter_by(id=athlete_id) \
            .first_or_404(description='Goalie with id {} is not attending the event {}'.format(athlete_id, game.id))
        game.goalies.remove(athlete)
        session.commit()
        return {'message': 'Goalie successfully removed from game ' + str(game.id)}, 204


class RefereesInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AthleteModel.query.filter(AthleteModel.games_refereed.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        if len(game.referees) < game.exp_referees_cnt:
            game.referees.append(athlete)
            session.commit()
            return {'game_id': game.id, 'athlete_id': athlete.id, 'role_id': AthleteRole.REFEREE}, 200
        else:
            return {'message': 'Could not add the referee to the game as it is already full ' + str(
                game.exp_referees_cnt)}, 404

    @staticmethod
    def delete(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query \
            .filter(AthleteModel.games_refereed.any(id=game.id)).filter_by(id=athlete_id) \
            .first_or_404(description='Referee with id {} is not refereeing the event {}'.format(athlete_id, game.id))
        game.referees.remove(athlete)
        session.commit()
        return {'message': 'Referee successfully removed from game ' + str(game.id)}, 204


class OrganizersInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AthleteModel.query.filter(AthleteModel.games_organized.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        game.organizers.append(athlete)
        session.commit()
        return {'game_id': game.id, 'athlete_id': athlete.id, 'role_id': AthleteRole.ORGANIZER}, 200

    @staticmethod
    def delete(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query \
            .filter(AthleteModel.games_organized.any(id=game.id)) \
            .filter_by(id=athlete_id) \
            .first_or_404(description='Organizer with id {} is not organizing the event {}'.format(athlete_id, game.id))
        game.players.remove(athlete)
        session.commit()
        return {'message': 'Player successfully removed from game ' + str(game.id)}, 204