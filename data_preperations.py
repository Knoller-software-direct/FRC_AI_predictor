import json
import numpy as np


def get_team_features(team, teams):
    return [
        teams[team]["rookie_year"],
        teams[team]["epa"],
        teams[team]["winrate"],
        teams[team]["average_rank"],
        teams[team]["average_pick"],
        teams[team]["average_match_score"],
        teams[team]["number_of_events"],
        teams[team]["average_match_score"],
        teams[team]["worlds_rate"],
        teams[team]["number_of_matches"],
        teams[team]["average_opponent_epa"],
        teams[team]["average_alliance_epa"]
    ]


def process_and_save(events, teams, output_x="x.npy", output_y="y.npy"):
    x = []
    y = []
    for event in events:
        for match in events[event]["matches"]:
            if match["red_score"] == match["blue_score"]:
                continue
            red_alliance = match["red_alliance"]
            blue_alliance = match["blue_alliance"]
            try:
                red_features = np.array([get_team_features(team, teams) for team in red_alliance])
                blue_features = np.array([get_team_features(team, teams) for team in blue_alliance])
            except KeyError as e:
                continue

            red_summary = np.concatenate([red_features.mean(axis=0), red_features.max(axis=0)])
            blue_summary = np.concatenate([blue_features.mean(axis=0), blue_features.max(axis=0)])

            feature_vector = np.concatenate([red_summary, blue_summary])
            x.append(feature_vector)
            y.append(1 if match["winner"] == "red" else 0)
    x = np.array(x)
    y = np.array(y)
    np.save(output_x, x)
    np.save(output_y, y)


f = open("teams.json", encoding="utf8")
teams = json.load(f)

f = open("events.json", encoding="utf8")
events = json.load(f)

process_and_save(events,teams, "training_data_features.npy","training_data_labels.npy")
