from app.core.model.models import IceRinkModel


class IceRinkHandler:
    @staticmethod
    def fetch_all():
        return IceRinkModel.query.all()

    @staticmethod
    def fetch(**kwargs):
        if 'id' in kwargs:
            return IceRinkModel.query.filter_by(id=kwargs.get('id')).first()
        # elif 'email' in kwargs:
        #     return AthleteModel.query.filter_by(email=kwargs.get('email')).first()
        else:
            raise ValueError("Unexpected argument has been provided to the fetch function - expected 'id' or 'login'")