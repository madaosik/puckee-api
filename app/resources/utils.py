from flask import current_app as app


def req_err_msg(missing_param: str, endpoint: str):
    return "\'" + missing_param + "\' has not been provided as GET parameter for " + endpoint


def check_paging_params(request_args: dict):
    if 'page_id' not in request_args:
        err_msg = req_err_msg('page_id', '/api/game')
        app.logger.error(err_msg)
        return {'message': err_msg}, 400
    elif 'per_page' not in request_args:
        err_msg = req_err_msg('per_page', '/api/game')
        app.logger.error(err_msg)
        return {'message': err_msg}, 400
    return None
