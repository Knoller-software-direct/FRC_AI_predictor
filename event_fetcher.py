import requests
import json
import time

AUTH_KEY = "zTmnnKUveaky77Kgv3waDEu6VPrqsMVKcpglKg2so4eey7UEv9uJFfuxGg54rvOj"


def fetch_event_keys(start_year, end_year, filename="event_keys.json"):
    event_keys = []
    for i in range(start_year, end_year + 1):
        print("fetching event keys from " + str(i))
        x = requests.get("https://www.thebluealliance.com/api/v3/events/" + str(i) + "/keys",
                         headers={"X-TBA-Auth-Key": AUTH_KEY})
        events = x.json()
        event_keys += events

    event_keys_json = {
        "event_keys": event_keys
    }

    with open(filename, "w") as outfile:
        outfile.write(json.dumps(event_keys_json, indent=4))
    return event_keys


def format_array(arr):
    return "[" + ",".join(f'"{item}"' for item in arr) + "]"


def process_matches(matches_json):
    matches = []
    for match_json in matches_json:
        match = (f'{{"blue_alliance":{format_array(match_json["alliances"]["blue"]["team_keys"])},' +
                 f'"red_alliance":{format_array(match_json["alliances"]["red"]["team_keys"])},' +
                 f'"red_score":{match_json["alliances"]["red"]["score"]},' +
                 f'"blue_score":{match_json["alliances"]["blue"]["score"]},' +
                 f'"winner":{"\"blue\"" if match_json["alliances"]["blue"]["score"] > match_json["alliances"]["red"]["score"] else "\"red\""}}}')
        matches.append(json.loads(match))

    return matches


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02}:{minutes:02}:{secs:02}:{milliseconds:03}"


def fetch_events(event_keys, filename="events.json", update_worlds=False):
    start = time.time()
    events = {}
    worlds_keys = []

    for event_key in event_keys["event_keys"]:
        event_data = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event_key}/simple',
                                  headers={"X-TBA-Auth-Key": AUTH_KEY}).json()
        if event_data["event_type"] > 4 or event_data["event_type"] < 0:
            print(f'skipping {event_key}')
            continue

        alliances_json = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event_key}/alliances',
                                      headers={"X-TBA-Auth-Key": AUTH_KEY}).json()
        if alliances_json is None:
            print(f'skipping {event_key}')
            continue

        alliances = []
        for alliance in alliances_json:
            alliances.append(alliance["picks"])

        if event_data["event_type"] == 3 and update_worlds:
            worlds_keys.append(event_key)

        matches_json = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple',
                                    headers={"X-TBA-Auth-Key": AUTH_KEY}).json()

        team_rankings_json = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event_key}/rankings',
                                          headers={"X-TBA-Auth-Key": AUTH_KEY}).json()["rankings"]
        team_rankings = []
        for i in range(len(team_rankings_json)):
            team_rankings.append(team_rankings_json[i]["team_key"])

        events[event_key] = {
            "matches": process_matches(matches_json),
            "teams": team_rankings,
            "alliances": alliances
        }
        print(f'fetched data from {event_key}')
    events = json.loads(json.dumps(events))

    with open(filename, "w") as outfile:
        outfile.write(json.dumps(events, indent=4))
    if update_worlds:
        with open("worlds_keys.json", "w") as outfile:
            outfile.write(json.dumps(worlds_keys, indent=4))

    end = time.time()
    print(format_time(end - start))


fetch_event_keys(2018, 2024, "event_keys.json")

f = open("event_keys.json", encoding="utf8")
event_keys = json.load(f)

fetch_events(event_keys, "events.json", update_worlds=True)
