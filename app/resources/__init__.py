from app.resources import base, event, athlete


def configure_apis(api):
    event.configure(api)
    athlete.configure(api)
