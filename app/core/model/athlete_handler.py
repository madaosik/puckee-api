from app.core.model.models import AthleteModel
from app.core.db_base import session
from sqlalchemy import exc as e


class AthleteHandler:
    @staticmethod
    def fetch_all():
        return AthleteModel.query.all()

    @staticmethod
    def fetch_by_id(athlete_id):
        return AthleteModel.query.filter_by(id=athlete_id)\
                .first_or_404(description='Athlete with id={} is not available'.format(athlete_id))

    @staticmethod
    def add(athlete):
        try:
            session.add(athlete)
            session.commit()
        except e.SQLAlchemyError:
            return {"message": "An error occurred creating the athlete."}, 500
        return athlete.json(), 201

    @staticmethod
    def delete(athlete_id: int):
        athlete = AthleteHandler.fetch_by_id(athlete_id)
        session.delete(athlete)
        session.commit()
        return {'message': 'Athlete has been deleted'}, 204

    @staticmethod
    def update(athlete_id: int, data: dict):
        athlete = AthleteHandler.fetch_by_id(athlete_id)
        athlete.__dict__.update(data)
        session.commit()
        return athlete.json()
