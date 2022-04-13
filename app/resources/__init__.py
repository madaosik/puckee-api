from app.resources import base, game, game_participants, athlete, auth, icerink


def configure_apis(api):
    # base.configure(api)
    game.configure(api)
    game_participants.configure(api)
    auth.configure(api)
    athlete.configure(api)
    icerink.configure(api)
