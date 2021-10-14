from app.api import base
from app.api import event


def configure_apis(api):
    event.configure(api)
