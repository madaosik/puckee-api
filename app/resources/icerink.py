from app.core.model.models import AthleteModel
from app.core.model import AthleteHandler, IceRinkHandler
from flask_restful import Resource, reqparse
from flask import current_app as app
from flask import request
from flask_jwt_extended import jwt_required


class IceRinks(Resource):
    @staticmethod
    # @jwt_required()
    def get():
        ret_arr = []
        for rink in IceRinkHandler.fetch_all():
            ret_arr.append({   'id': rink.id,
                                'name': rink.name,
                                'address': rink.address,
                                'price_per_hour': rink.price_per_hour }
                            )

        return ret_arr, 200

    # @staticmethod
    # # @jwt_required()
    # def post():
    #     app.logger.info(f'parsed args: {IceRink.parser.parse_args()}')
    #     data = IceRink.parser.parse_args()
    #     return AthleteHandler.add(data)


class IceRink(Resource):
    @staticmethod
    # @jwt_required()
    def get(rink_id: int):
        rink = IceRinkHandler.fetch(id=rink_id)
        if not rink:
            return {'message': 'Rink with the requested id ' + str(rink_id) + ' could not be found!'}, 404
        return {'id': rink.id, 'name': rink.name, 'address': rink.address, 'price_per_hour': rink.price_per_hour}, 200

def configure(api):
    api.add_resource(IceRinks, '/api/icerink')
    api.add_resource(IceRink, '/api/icerink/<rink_id>')