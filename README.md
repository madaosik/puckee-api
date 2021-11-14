# teamorg-server
REST API for Team Sports Organization applications

## API description

### /api/athlete
Athlete (user in general) creation or retrieval
- **GET** - returns all the registered users (currently without their roles - player, goalie, referee - TBD)
- **POST** - creates a new athlete (user)
  - Requires 'login', 'password', 'name' and 'email' parameters

### /api/event
Events creation/retrieval
- **GET**
- **POST**
  - Requires:
    - *'name'*
    - *'organizer_id'*
    - *'total_places'*
    - *'start'* - start of the event in format '**YYYY-MM-DD**T**HH:MM:SS**'
    - *'duration'* - duration of the event in format '**HH:MM:SS**'
    - *'exp_level'* - integer value from 1 to 6

### /api/event/<event_id>
Specific event update/removal
- **GET** - retrieves the event with id <event_id> along with all the participants' details
- **DELETE** - deletes the event with id <event_id>
- **PUT** - updates the event with id <event_id>
  - Requires: see /api/event

### /api/event/<event_id>/participants
- **GET** - returns all the participants of the event <event_id>, grouped by their role (player, organizer, referee, goalie)
- **POST** - adds a new participant to the event <event_id>
  - Requires *'athlete_id'* and *'athlete_role'* parameters
- **DELETE** - removes the participant from the given event
  - Requires *'athlete_id'* and *'athlete_role'* parameters (athlete role probably redundant, as in one match only one role can be fulfilled - TBD)