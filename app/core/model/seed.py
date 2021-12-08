from faker import Faker
from alembic import op
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

from app.core.model.models import DATETIME_FORMAT, DURATION_FORMAT, EVENT_NAME_LEN_LIMIT, \
    AthleteModel, AthleteRoleModel, athlete_roles, GameModel, \
    event_players, event_organizers, event_goalies, event_referees

ATHLETES_CNT = 100
EVENTS_CNT = 100
PLAYERS_CNT = 50
# Every fifth athlete is a goalie
GOALIE_FREQ = 5
GOALIE_MAX_CNT = 2
# Every 13th athlete is a referee
REF_FREQ = 13
REF_MAX_CNT = 3


def seed_data():
    athlete_role_table = AthleteRoleModel.__table__
    op.bulk_insert(athlete_role_table, [{'role': 'user'}, {'role': 'player'}, {'role': 'goalie'}, {'role': 'referee'}])

    athlete_table = AthleteModel.__table__
    Faker.seed(0)
    fake = Faker()
    athletes = []

    # Seeding all the athletes
    passwd = 'passwd'
    athlete_dict = {'password_hash': generate_password_hash(passwd, method='sha256'),
                    'name': 'Adam Tester',
                    'email': 'a@a.com',
                    'perf_level': '4'}
    athletes.append(athlete_dict)
    for i in range(2, ATHLETES_CNT + 1):
        passwd = 'pass' + str(i)
        athlete_dict = {'password_hash': generate_password_hash(passwd, method='sha256'),
                        'name': fake.name(),
                        'email': fake.ascii_email(),
                        'perf_level': random.randint(1, 6)}
        athletes.append(athlete_dict)
    op.bulk_insert(athlete_table, athletes)
    print('Athletes successfully seeded!')

    # Seeding the user, player, goalie and referee roles
    roles_rel = []
    for i in range(1, ATHLETES_CNT + 1):
        role_user = {'role_id': 1, 'athlete_id': i}
        roles_rel.append(role_user)
        if (i < 51) or (i % 2 == 0):
            role_player = {'role_id': 2, 'athlete_id': i}
            roles_rel.append(role_player)
        if i % GOALIE_FREQ == 0:
            role_goalie = {'role_id': 3, 'athlete_id': i}
            roles_rel.append(role_goalie)
        if i % REF_FREQ == 0:
            role_referee = {'role_id': 4, 'athlete_id': i}
            roles_rel.append(role_referee)
    op.bulk_insert(athlete_roles, roles_rel)
    print('Athlete roles successfully seeded!')

    # Seeding the events
    events = []
    for i in range(1, EVENTS_CNT + 1):
        if i % 2 == 0:
            duration = "01:00:00"
        elif i % 9 == 0:
            duration = "01:30:00"
        else:
            duration = "01:15:00"
        exp_level = random.randrange(1, 7)

        start_time = fake.date_time_between(start_date=datetime(2021, 11, 30, 00, 00, 00),
                                            end_date=datetime(2022, 1, 31, 00, 00, 00))
        start_time_rounded = start_time + (datetime.min - start_time) % timedelta(minutes=15)
        while True:
            event_name = fake.catch_phrase()
            if len(event_name) < EVENT_NAME_LEN_LIMIT:
                break
            else:
                event_name = fake.catch_phrase()

        locations = ['Sportcentrum Lužánky', 'winninggroup Arena', 'TJ Stadion Brno', 'Hokejová hala Úvoz']
        location = random.choice(locations)

        event = {'name': event_name,
                 'total_places': random.randrange(2, 4)*10,
                 'start': start_time_rounded,
                 'duration': datetime.strptime(duration, DURATION_FORMAT),
                 'location': location,
                 'exp_level': exp_level
                 }
        events.append(event)

    events_table = GameModel.__table__
    op.bulk_insert(events_table, events)
    print('Events successfully seeded!')

    player_events_rel = []
    goalie_events_rel = []
    ref_events_rel = []
    organizer_events_rel = []

    for event_id in range(1, EVENTS_CNT + 1):
        # Seeding the players signed up of events (between 7 and 20)
        players_ind = random.sample(range(1, int(PLAYERS_CNT/2) + 1), random.randrange(7, 20))
        # We want to have 1-2 organizers
        organizers_ind = random.sample(range(1, ATHLETES_CNT), random.randrange(1, 3))

        # We want to have 0-3 goalies
        goalies_ind = random.sample(range(0, ATHLETES_CNT, GOALIE_FREQ), random.randrange(0, GOALIE_MAX_CNT+1))
        # Replace non-existing goalie with id 0
        goalies_ind = [random.randrange(GOALIE_FREQ, PLAYERS_CNT, GOALIE_FREQ) if x == 0 else x for x in goalies_ind]
        # For duplicit values removal
        goalies_ind = list(set(goalies_ind))


        # We want to have REF_MAX_CNT referees
        referee_ind = random.sample(range(0, ATHLETES_CNT, REF_FREQ), random.randrange(0, REF_MAX_CNT+1))
        # Replace non-existing referee with id 0
        referee_ind = [random.randrange(REF_FREQ, PLAYERS_CNT, REF_FREQ) if x == 0 else x for x in referee_ind]
        # For duplicit values removal
        referee_ind = list(set(referee_ind))

        for player_id in players_ind:
            player_event = {'event_id': int(event_id), 'athlete_id': int(player_id)}
            player_events_rel.append(player_event)

        for goalie_id in goalies_ind:
            goalie_event = {'athlete_id': goalie_id, 'event_id': event_id}
            goalie_events_rel.append(goalie_event)

        for organizer_id in organizers_ind:
            organizers_event = {'athlete_id': organizer_id, 'event_id': event_id}
            organizer_events_rel.append(organizers_event)

        for ref_id in referee_ind:
            ref_event = {'athlete_id': ref_id, 'event_id': event_id}
            ref_events_rel.append(ref_event)

    op.bulk_insert(event_players, player_events_rel)
    op.bulk_insert(event_goalies, goalie_events_rel)
    op.bulk_insert(event_organizers, organizer_events_rel)
    op.bulk_insert(event_referees, ref_events_rel)
    print('Event participants successfully seeded!')
