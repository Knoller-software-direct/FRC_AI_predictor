import statbotics
import json

sb = statbotics.Statbotics()


def get_pick_from_alliance(alliance, pick_order):
    if pick_order == 0:
        return 1 + (alliance - 1) * 2
    if pick_order == 1:
        return alliance * 2
    return 16 + (9 - alliance)


def get_teams_from_sb():
    teams = []
    for i in range(4):
        teams += sb.get_teams(limit=1000, offset=1000 * i, active=True)
    for i in range(5):
        teams += sb.get_teams(limit=1000, offset=1000 * i, active=False)
    with open('sb_teams.json', 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=4)


f = open("sb_teams.json", encoding="utf8")
sb_teams = json.load(f)
teams = "{"

f = open("events.json", encoding="utf8")
events = json.load(f)

f = open("worlds_keys.json", encoding="utf8")
worlds = json.load(f)

f = open("max_scores.json", encoding="utf8")
max_scores = json.load(f)

for team in sb_teams:
    if team["norm_epa"] is None:
        continue
    team_json = (f'"frc{team["team"]}":{{'
                 f'"rookie_year":{team["rookie_year"] if team["rookie_year"] is not None else 2024},'
                 f'"epa":{team["norm_epa"]},'
                 f'"winrate": 0,'
                 '"average_rank": 0.0,'
                 '"average_pick": 0.0,'
                 '"number_of_events": 0,'
                 '"average_match_score": 0.0,'
                 '"worlds_rate": 0.0,'
                 f'"number_of_matches": 0,'
                 '"average_opponent_epa": 0.0,'
                 '"average_alliance_epa": 0.0'
                 '},')
    teams += team_json

teams = json.loads(teams[:len(teams) - 1] + "}")

for event in events:
    event_teams = events[event]["teams"]
    if event_teams is None or len(event_teams) < 6:
        continue
    event_in_worlds = False
    if event in worlds:
        event_in_worlds = True
    rank = 1
    for team in event_teams:
        teams[team]["number_of_events"] += 1
        teams[team]["average_rank"] += rank
        rank += 1
        if event_in_worlds:
            teams[team]["worlds_rate"] += 1

    alliance_rank = 0
    for alliance in events[event]["alliances"]:
        alliance_rank += 1
        try:
            teams[alliance[0]]["average_pick"] += 1 + (alliance_rank - 1) * 2
            teams[alliance[1]]["average_pick"] += alliance_rank * 2
            teams[alliance[2]]["average_pick"] += 16 + (9 - alliance_rank)
        except:
            continue
        for team in alliance:
            try:
                event_teams.remove(team)
            except:
                continue
    for team in event_teams:
        teams[team]["average_pick"] += 25
    for match in events[event]["matches"]:
        try:
            blue_epa = teams[match["blue_alliance"][0]]["epa"] + teams[match["blue_alliance"][1]]["epa"] + \
                       teams[match["blue_alliance"][2]]["epa"]
            red_epa = teams[match["red_alliance"][0]]["epa"] + teams[match["red_alliance"][1]]["epa"] + \
                      teams[match["red_alliance"][2]]["epa"]
            for team in match["blue_alliance"]:
                if match["winner"] == "blue":
                    teams[team]["winrate"] += 1
                teams[team]["number_of_matches"] += 1
                teams[team]["average_match_score"] += match["blue_score"] / max_scores[event[:4]]
                teams[team]["average_opponent_epa"] += red_epa
                teams[team]["average_alliance_epa"] += blue_epa
            for team in match["red_alliance"]:
                if match["winner"] == "red":
                    teams[team]["winrate"] += 1
                teams[team]["number_of_matches"] += 1
                teams[team]["average_match_score"] += match["red_score"] / max_scores[event[:4]]
                teams[team]["average_opponent_epa"] += blue_epa
                teams[team]["average_alliance_epa"] += red_epa
        except:
            continue

for team in teams:
    if teams[team]["number_of_matches"] > 0:
        teams[team]["winrate"] /= teams[team]["number_of_matches"]
        teams[team]["average_match_score"] /= teams[team]["number_of_matches"]
        teams[team]["average_alliance_epa"] /= (teams[team]["number_of_matches"] * 3)
        teams[team]["average_opponent_epa"] /= (teams[team]["number_of_matches"] * 3)

    if teams[team]["rookie_year"] <= 2018:
        teams[team]["worlds_rate"] /= 5
    elif teams[team]["rookie_year"] == 2019:
        teams[team]["worlds_rate"] /= 4
    elif teams[team]["rookie_year"] <= 2021:
        teams[team]["worlds_rate"] /= 3
    elif teams[team]["rookie_year"] == 2025:
        teams[team]["worlds_rate"] = 0
    else:
        teams[team]["worlds_rate"] /= 2025 - teams[team]["rookie_year"]

    if teams[team]["number_of_events"] != 0:
        teams[team]["average_rank"] /= teams[team]["number_of_events"]
        teams[team]["average_pick"] /= teams[team]["number_of_events"]

with open("teams.json", "w") as outfile:
    outfile.write(json.dumps(teams, indent=4))
