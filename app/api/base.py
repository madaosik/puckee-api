from flask import make_response, jsonify


def configure(app):
    @app.errorhandler(404)
    def page_not_found(e):
        response = make_response(
            jsonify(
                {"message": "Resource not found!"}
            ),
            404,
        )
        response.headers["Content-Type"] = "application/json"
        return response

    @app.errorhandler(403)
    def forbidden(e):
        response = make_response(
            jsonify(
                {"message": "You are not allowed to see this!"}
            ),
            403,
        )
        response.headers["Content-Type"] = "application/json"
        return response

    @app.route('/')
    def home_redir():
        response = make_response(
            jsonify(
                {"message": "Please specify API point!"}
            ),
            404,
        )
        response.headers["Content-Type"] = "application/json"
        return response
