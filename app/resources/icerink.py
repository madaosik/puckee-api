from app.core.model.models import AthleteModel
from app.core.model import AthleteHandler, IceRinkHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required


class IceRink(Resource):
    @staticmethod
    # @jwt_required()
    def get():
        ret_dict = {}
        for rink in IceRinkHandler.fetch_all():
            ret_dict[rink.id] = {'name': rink.name,
                                 'address': rink.address,
                                 'price_per_hour': rink.price_per_hour }

        return ret_dict, 200

    # @staticmethod
    # # @jwt_required()
    # def post():
    #     app.logger.info(f'parsed args: {IceRink.parser.parse_args()}')
    #     data = IceRink.parser.parse_args()
    #     return AthleteHandler.add(data)


def configure(api):
    api.add_resource(IceRink, '/api/icerink')