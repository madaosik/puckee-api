from app.resources import base
from app.resources import event


def configure_apis(api):
    event.configure(api)
