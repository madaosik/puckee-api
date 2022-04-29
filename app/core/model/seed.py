from faker import Faker
from alembic import op
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta
from app.core.model.attendance_handler import AthleteRole
from app.core.model.models import GAME_NAME_LEN_LIMIT, \
    AthleteModel, AthleteRoleModel, AthleteRoleAssociationModel, GameModel, IceRinkModel, \
    game_players, game_anonym_players, game_organizers, game_goalies, game_anonym_goalies, game_referees, \
    game_anonym_referees, FollowersModel, AnonymousAthleteModel

GAMES_CNT = 300
ATHLETES_CNT = 400
ANONYM_ATHLETES_CNT = int(ATHLETES_CNT/8)
PLAYERS_CNT = 300

# Every fifth athlete is a goalie
GOALIE_FREQ = 5
GOALIE_MAX_CNT = 2

# Every 13th athlete is a referee
REF_FREQ = 13
REF_MAX_CNT = 3

# Every athlete follows every 5th athlete
FOLLOWING_FREQ = 6
# There is 20% probability that the follow relationship is "opt_out"
OPT_OUT_MODE_PROB = 0.2


# outputs True or False probabilistically based on the input of a random number from 0 to 1
def decision(probability):
    return random.random() < probability


def seed_data():
    athlete_role_table = AthleteRoleModel.__table__
    op.bulk_insert(athlete_role_table, [{'role': 'user'},
                                        {'role': 'player'},
                                        {'role': 'goalie'},
                                        {'role': 'referee'}
                                        ])

    ice_rink_table = IceRinkModel.__table__
    ice_rink_array = [{'name': 'Sportcentrum Lužánky - NHL', 'address': '', 'price_per_hour': 3960},
                {'name': 'Sportcentrum Lužánky - Evropská', 'address': '', 'price_per_hour': 3960},
                {'name': 'Hokejová hala ZŠ Úvoz', 'address': '', 'price_per_hour': 3450},
                {'name': 'Winning Group Arena', 'address': '', 'price_per_hour': 4250},
                {'name': 'Zimní stadion Kuřim', 'address': '', 'price_per_hour': 3850},
                {'name': 'Zimní stadion Rosice', 'address': '', 'price_per_hour': 3400},
                {'name': 'Zimní stadion Velká Bíteš', 'address': '', 'price_per_hour': 3350},
                {'name': 'Zimní stadion Blansko', 'address': '', 'price_per_hour': 3550},
                {'name': 'Zimní stadion Vyškov', 'address': '', 'price_per_hour': 3750},
                ]
    op.bulk_insert(ice_rink_table, ice_rink_array)
    Faker.seed(0)
    fake = Faker()

    #####################################################################################################
    #####################################################################################################
    # Seeding all the athletes
    athlete_table = AthleteModel.__table__
    athletes = []

    passwd = 'passwd'
    athlete_dict = {'password_hash': generate_password_hash(passwd, method='sha256'),
                    'name': 'Adam Tester',
                    'email': 'a@a.com',
                    }
    athletes.append(athlete_dict)
    athlete_dict = {'password_hash': generate_password_hash(passwd, method='sha256'),
                    'name': 'Adam Bi-roled',
                    'email': 'b@b.com',
                    }
    athletes.append(athlete_dict)

    for i in range(3, ATHLETES_CNT + 1):
        passwd = 'pass' + str(i)
        athlete_dict = {'password_hash': generate_password_hash(passwd, method='sha256'),
                        'name': fake.name(),
                        'email': fake.ascii_email(),
                        }
        athletes.append(athlete_dict)
    op.bulk_insert(athlete_table, athletes)
    print('Athletes successfully seeded!')

    #######################################################################################################
    #######################################################################################################
    # Seeding the user, player, goalie and referee roles
    roles_rel = []

    # Athlete 1 has fixed roles - user and player
    role_user_1 = {'role_id': int(AthleteRole.USER), 'athlete_id': 1, 'skill_level': 0.0}
    roles_rel.append(role_user_1)
    role_player_1 = {'role_id': int(AthleteRole.PLAYER), 'athlete_id': 1, 'skill_level': 4.0}
    roles_rel.append(role_player_1)

    # Athlete 2 has fixed roles - user, player and goalie
    role_user_2 = {'role_id': int(AthleteRole.USER), 'athlete_id': 2, 'skill_level': 0.0}
    roles_rel.append(role_user_2)
    role_player_2 = {'role_id': int(AthleteRole.PLAYER), 'athlete_id': 2, 'skill_level': 3.5}
    roles_rel.append(role_player_2)
    role_goalie_2 = {'role_id': int(AthleteRole.GOALIE), 'athlete_id': 2, 'skill_level': 1.5}
    roles_rel.append(role_goalie_2)

    # Now let's seed the roles of the rest of athletes
    for i in range(3, ATHLETES_CNT + 1):
        # Every athlete is a user
        role_user = {'role_id': int(AthleteRole.USER), 'athlete_id': i, 'skill_level': 0.0}
        roles_rel.append(role_user)

        # First ATHLETES_CNT/2 athletes are players and then there are some additional ones
        if (i < (int(ATHLETES_CNT/2) + 1)) or (i % 2 == 0):
            role_player = {'role_id': int(AthleteRole.PLAYER), 'athlete_id': i, 'skill_level': random.uniform(1.0, 6.0)}
            roles_rel.append(role_player)

        # Every GOALIE_FREQ athlete is a goalie
        if i % GOALIE_FREQ == 0:
            role_goalie = {'role_id': int(AthleteRole.GOALIE), 'athlete_id': i, 'skill_level': random.uniform(1.0, 6.0)}
            roles_rel.append(role_goalie)

        # Every REF_FREQ athlete is a referee
        if i % REF_FREQ == 0:
            role_referee = {'role_id': int(AthleteRole.REFEREE), 'athlete_id': i, 'skill_level': 0.0}
            roles_rel.append(role_referee)
    athlete_roles = AthleteRoleAssociationModel.__table__
    op.bulk_insert(athlete_roles, roles_rel)
    print('Athlete roles successfully seeded!')

    # Seeding follow relationships
    follow_rel = []
    for i in range(1, ATHLETES_CNT + 1):
        # Every athlete follows 20% random others
        followees = random.sample(range(1, ATHLETES_CNT + 1), int(ATHLETES_CNT/FOLLOWING_FREQ))
        for followee in followees:
            rel_dict = {'from_id': i, 'to_id': followee, 'opt_out_mode': decision(OPT_OUT_MODE_PROB)}
            follow_rel.append(rel_dict)

    followers_table = FollowersModel.__table__
    op.bulk_insert(followers_table, follow_rel)
    print('Follow relationships successfully seeded!')

    #####################################################################################################
    #####################################################################################################
    # Creating the events

    events = []
    for i in range(1, GAMES_CNT + 1):
        exp_skill = random.randrange(1, 7)
        start_datetime = fake.date_time_between(start_date=datetime(2022, 4, 1, 00, 00, 00),
                                                end_date=datetime(2022, 6, 22, 00, 00, 00))
        start_datetime_rounded = start_datetime + (datetime.min - start_datetime) % timedelta(minutes=15)

        if i % 2 == 0:
            duration = timedelta(hours=1)
        elif i % 9 == 0:
            duration = timedelta(hours=1, minutes=15)
        else:
            duration = timedelta(hours=1, minutes=30)

        end_datetime_rounded = start_datetime_rounded + duration
        start_time = start_datetime_rounded
        end_time = end_datetime_rounded
        # game_date = start_datetime_rounded.date()


        while True:
            event_name = fake.catch_phrase()
            if len(event_name) < GAME_NAME_LEN_LIMIT:
                break
            else:
                event_name = fake.catch_phrase()

        event = {'name': event_name,
                 'exp_players_cnt': random.randrange(2, 4)*10,
                 'exp_goalies_cnt': random.randrange(1, 3),
                 'goalie_renum': random.choice([0, 50, 150, 200]),
                 'exp_referees_cnt': random.randrange(1, 3),
                 'referee_renum': random.choice([0, 50, 150, 200]),
                 'location_id': random.randrange(1, len(ice_rink_array) + 1),
                 # 'date': game_date,
                 'start_time': start_time,
                 'end_time': end_time,
                 'exp_skill': exp_skill,
                 'est_price': random.choice([200, 250, 300]),
                 'other_costs': random.choice([50, 100, 0, 150, 200]),
                 'remarks': fake.paragraph(nb_sentences=3)
                 }
        events.append(event)

    events_table = GameModel.__table__
    op.bulk_insert(events_table, events)
    print('Events successfully seeded!')

    #####################################################################################################
    #####################################################################################################

    # Seeding anonymous athletes
    anonym_athlete_table = AnonymousAthleteModel.__table__
    anonym_athletes = []
    for i in range(1, ANONYM_ATHLETES_CNT + 1):
        anonym_athlete_dict = {'name': fake.name(),
                               'added_by': random.randrange(1, ATHLETES_CNT + 1),
                               'added_in': random.randrange(1, GAMES_CNT + 1),
                                }
        anonym_athletes.append(anonym_athlete_dict)
    op.bulk_insert(anonym_athlete_table, anonym_athletes)
    print('Anonymous athletes successfully seeded!')

    #####################################################################################################
    #####################################################################################################
    # Seeding the event participants

    player_events_rel = []
    anonym_player_events_rel = []
    goalie_events_rel = []
    anonym_goalie_events_rel = []
    ref_events_rel = []
    anonym_referee_events_rel = []
    organizer_events_rel = []

    for event_id in range(1, GAMES_CNT + 1):
        # We want to have 1-2 organizers
        organizers_ind = random.sample(range(1, ATHLETES_CNT), random.randrange(1, 4))

        # Seeding the players signed up of events (between 7 and 16)
        players_ind = random.sample(range(1, int(PLAYERS_CNT/2) + 1), random.randrange(7, 17))
        # Seeding the anonymous players added for the events (between 1 and 4)
        anonym_players_ind = random.sample(range(1, ANONYM_ATHLETES_CNT + 1), random.randrange(1, 5))

        # We want to have 0-1 registered goalies and 0-1 unregistered ones
        goalies_ind = random.sample(range(0, ATHLETES_CNT, GOALIE_FREQ), random.randrange(0, GOALIE_MAX_CNT))
        # Starting index of range is 1 because anonymous athletes are not assigned any roles whatsoever
        # (no need to skip indexes)
        anonym_goalies_ind = random.sample(range(1, ANONYM_ATHLETES_CNT), random.randrange(0, GOALIE_MAX_CNT))

        # Replace non-existing goalie with id 0
        goalies_ind = [random.randrange(GOALIE_FREQ, PLAYERS_CNT, GOALIE_FREQ) if x == 0 else x for x in goalies_ind]
        # anonym_goalies_ind = [random.randrange(GOALIE_FREQ, PLAYERS_CNT, GOALIE_FREQ) if x == 0 else x for x in anonym_goalies_ind]
        # For duplicit values removal
        goalies_ind = list(set(goalies_ind))
        anonym_goalies_ind = list(set(anonym_goalies_ind))

        # We want to have 0-1 registered referees and 0-1 unregistered ones
        referee_ind = random.sample(range(0, ATHLETES_CNT, REF_FREQ), random.randrange(0, REF_MAX_CNT-1))
        # Starting index of range is 1 because anonymous athletes are not assigned any roles whatsoever
        # (no need to skip indexes)
        anonym_referee_ind = random.sample(range(1, ANONYM_ATHLETES_CNT), random.randrange(0, REF_MAX_CNT - 1))
        # Replace non-existing referee with id 0
        referee_ind = [random.randrange(REF_FREQ, PLAYERS_CNT, REF_FREQ) if x == 0 else x for x in referee_ind]
        # For duplicit values removal
        referee_ind = list(set(referee_ind))
        anonym_referee_ind = list(set(anonym_referee_ind))

        for player_id in players_ind:
            player_event = {'game_id': int(event_id), 'athlete_id': int(player_id)}
            player_events_rel.append(player_event)

        for player_id in anonym_players_ind:
            anonym_player_event = {'game_id': int(event_id), 'anonym_id': int(player_id)}
            anonym_player_events_rel.append(anonym_player_event)

        for goalie_id in goalies_ind:
            goalie_event = {'athlete_id': goalie_id, 'game_id': event_id}
            goalie_events_rel.append(goalie_event)

        for goalie_id in anonym_goalies_ind:
            anonym_goalie_event = {'anonym_id': goalie_id, 'game_id': event_id}
            anonym_goalie_events_rel.append(anonym_goalie_event)

        for organizer_id in organizers_ind:
            organizers_event = {'athlete_id': organizer_id, 'game_id': event_id}
            organizer_events_rel.append(organizers_event)

        for ref_id in referee_ind:
            ref_event = {'athlete_id': ref_id, 'game_id': event_id}
            ref_events_rel.append(ref_event)

        for ref_id in anonym_referee_ind:
            anonym_referee_event = {'anonym_id': ref_id, 'game_id': event_id}
            anonym_referee_events_rel.append(anonym_referee_event)

    op.bulk_insert(game_organizers, organizer_events_rel)
    op.bulk_insert(game_players, player_events_rel)
    op.bulk_insert(game_anonym_players, anonym_player_events_rel)
    op.bulk_insert(game_goalies, goalie_events_rel)
    op.bulk_insert(game_anonym_goalies, anonym_goalie_events_rel)
    op.bulk_insert(game_referees, ref_events_rel)
    op.bulk_insert(game_anonym_referees, anonym_referee_events_rel)

    print('Event participants successfully seeded!')



