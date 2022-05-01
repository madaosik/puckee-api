from app.core.model.models import AthleteModel, GameModel, AnonymousAthleteModel, AthleteRole
from app.core.db_base import session
from app.core.model.athlete_handler import AnonymousAthleteHandler


class PlayersInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AthleteModel.query.filter(AthleteModel.games_played.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, athlete_id: int):
        athlete = AthleteModel.query.filter_by(id=athlete_id) \
            .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))
        if len(game.players + game.anonym_players) < game.exp_players_cnt:
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


class AnonymPlayersInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AnonymousAthleteModel.query.filter(AnonymousAthleteModel.games_anonym_played.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, data: dict):
        """
        Adds anonymous player to a game
        @param game: GameModel
        @param data: dict Contains 'athlete_name' and 'requesting_id' keys
        """
        if (len(game.players) + len(game.anonym_players)) >= game.exp_players_cnt:
            return {'message': 'Could not add the anonym player to the game as it is already full '
                               + str(game.exp_players_cnt)}, 404

        athlete = AnonymousAthleteHandler.fetch(data['athlete_name'], game.id, data['requesting_id'])
        game.anonym_players.append(athlete)
        session.commit()
        return {'game_id': game.id, 'anonym_athlete_name': athlete.name, 'role_id': AthleteRole.PLAYER}, 200


    @staticmethod
    def delete(game: GameModel, athlete_name: str):
        athlete = AnonymousAthleteModel.query \
            .filter(AnonymousAthleteModel.games_anonym_played.any(id=game.id)).filter_by(name=athlete_name) \
            .first_or_404(description='Athlete with id {} is not playing the event {}'.format(athlete_name, game.id))
        game.anonym_players.remove(athlete)
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


class AnonymGoaliesInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AnonymousAthleteModel.query.filter(AnonymousAthleteModel.games_anonym_goalied.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, data: dict):
        """
        Adds anonymous goalie to a game
        @param game: GameModel
        @param data: dict Contains 'athlete_name' and 'requesting_id' keys
        """
        if (len(game.goalies) + len(game.anonym_goalies)) >= game.exp_goalies_cnt:
            return {'message': 'Could not add the anonym player to the game as it is already full '
                               + str(game.exp_goalies_cnt)}, 404

        athlete = AnonymousAthleteHandler.fetch(data['athlete_name'], game.id, data['requesting_id'])
        game.anonym_goalies.append(athlete)
        session.commit()
        return {'game_id': game.id, 'anonym_athlete_name': athlete.name, 'role_id': AthleteRole.PLAYER}, 200

    @staticmethod
    def delete(game: GameModel, athlete_name: str):
        athlete = AnonymousAthleteModel.query \
            .filter(AnonymousAthleteModel.games_anonym_goalied.any(id=game.id)).filter_by(name=athlete_name) \
            .first_or_404(description='Goalie with id {} is not attending the event {}'.format(athlete_name, game.id))
        game.anonym_goalies.remove(athlete)
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


class AnonymRefereesInGame:
    @staticmethod
    def fetch_all(game_id: int):
        return AnonymousAthleteModel.query.filter(AnonymousAthleteModel.games_anonym_refereed.any(id=game_id)).all()

    @staticmethod
    def add(game: GameModel, data: dict):
        """
        Adds anonymous referee to a game
        @param game: GameModel
        @param data: dict Contains 'athlete_name' and 'requesting_id' keys
        """
        if (len(game.referees) + len(game.anonym_referees)) >= game.exp_referees_cnt:
            return {'message': 'Could not add the anonym player to the game as it is already full '
                               + str(game.exp_referees_cnt)}, 404

        athlete = AnonymousAthleteHandler.fetch(data['athlete_name'], game.id, data['requesting_id'])
        game.anonym_referees.append(athlete)
        session.commit()
        return {'game_id': game.id, 'anonym_athlete_name': athlete.name, 'role_id': AthleteRole.PLAYER}, 200

    @staticmethod
    def delete(game: GameModel, athlete_name: str):
        athlete = AnonymousAthleteModel.query \
            .filter(AnonymousAthleteModel.games_anonym_refereed.any(id=game.id)).filter_by(name=athlete_name) \
            .first_or_404(description='Referee with id {} is not refereeing the event {}'.format(athlete_name, game.id))
        game.anonym_referees.remove(athlete)
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