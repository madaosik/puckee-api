from app.resources import base, game, athlete, auth, icerink


def configure_apis(api):
    # base.configure(api)
    game.configure(api)
    auth.configure(api)
    athlete.configure(api)
    icerink.configure(api)
