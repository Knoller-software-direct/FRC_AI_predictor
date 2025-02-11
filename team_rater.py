import csv
import json
import requests

from ai_predictor import predict_matches_scores
from constants import AUTH_KEY

with open("teams.json", "r") as file:
    teams = json.load(file)


def get_teams_from_sb_csv(filename):
    num_values = []
    try:
        with open(filename, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            if 'num' not in reader.fieldnames:
                print(f"Error: 'num' column not found. Found columns: {reader.fieldnames}")
                return []

            for row in reader:
                try:
                    num_values.append("frc" + str(int(row['num'].strip())))
                except ValueError:
                    print(f"Warning: Non-integer value found in 'num' column: {row['num']}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return num_values


def rating_function(chance_to_beat_average_alliance):
    if chance_to_beat_average_alliance >= 1 or chance_to_beat_average_alliance <= 0:
        return -1
    return 1.0 / (1.0 - chance_to_beat_average_alliance) - 1.0
    # f(x) = 1/(1-x) - 1. when x -> 0 f(x) -> 0 when f(x) -> 1 f(x) -> infinity


def get_average_team(rateable_teams):
    year = 0.0
    epa = 0.0
    winrate = 0.0
    average_rank = 0.0
    average_pick = 0.0
    number_of_events = 0.0
    average_match_score = 0.0
    worlds_rate = 0.0
    number_of_matches = 0.0
    average_opponent_epa = 0.0
    average_alliance_epa = 0.0

    for team in rateable_teams:
        try:
            year += teams[team]["rookie_year"]
            epa += teams[team]["epa"]
            winrate += teams[team]["winrate"]
            average_rank += teams[team]["average_rank"]
            average_pick += teams[team]["average_pick"]
            number_of_events += teams[team]["number_of_events"]
            average_match_score += teams[team]["average_match_score"]
            worlds_rate += teams[team]["worlds_rate"]
            number_of_matches += teams[team]["number_of_matches"]
            average_opponent_epa += teams[team]["average_opponent_epa"]
            average_alliance_epa += teams[team]["average_alliance_epa"]
        except KeyError:
            year += 2025
            epa += 1450
            winrate += 0
            average_rank += 25
            average_pick += 25
            number_of_events += 0
            average_match_score += 0
            worlds_rate += 0
            number_of_matches += 0
            average_opponent_epa += 1450
            average_alliance_epa += 1450

    year /= len(rateable_teams)
    epa /= len(rateable_teams)
    winrate /= len(rateable_teams)
    average_rank /= len(rateable_teams)
    average_pick /= len(rateable_teams)
    number_of_events /= len(rateable_teams)
    average_match_score /= len(rateable_teams)
    worlds_rate /= len(rateable_teams)
    number_of_matches /= len(rateable_teams)
    average_opponent_epa /= len(rateable_teams)
    average_alliance_epa /= len(rateable_teams)

    team_json = (f'"average_team":{{'
                 f'"rookie_year":{year},'
                 f'"epa":{epa},'
                 f'"winrate": {winrate},'
                 f'"average_rank": {average_rank},'
                 f'"average_pick": {average_pick},'
                 f'"number_of_events": {number_of_events},'
                 f'"average_match_score": {average_match_score},'
                 f'"worlds_rate": {worlds_rate},'
                 f'"number_of_matches": {number_of_matches},'
                 f'"average_opponent_epa":{average_opponent_epa},'
                 f'"average_alliance_epa": {average_alliance_epa}'
                 '}')

    return team_json


def rate_teams(rateable_teams):
    matches = []
    teams_scores = {team: [0, 0.0] for team in rateable_teams}

    for team in rateable_teams:
        matches.append([[team, team, team], ["average_team", "average_team", "average_team"]])
    scores = predict_matches_scores(matches)

    for i in range(len(scores)):
        teams_scores[matches[i][0][0]][1] += rating_function(float(scores[i][0]))
    teams_scores = sorted(teams_scores.items(), key=lambda item: item[1], reverse=True)

    teams_scores = {key: [index + 1, value[1]] for index, (key, value) in enumerate(teams_scores)}
    return teams_scores


def create_rating_file(teams_csv, filename):
    teams = get_teams_from_sb_csv(teams_csv)
    teams_rating = rate_teams(teams)

    with open(filename, "w") as outfile:
        json.dump(teams_rating, outfile)

# teams_isr = requests.get(f'https://www.thebluealliance.com/api/v3/district/2025isr/teams/keys',
#                          headers={"X-TBA-Auth-Key": AUTH_KEY}).json()

# rateable_teams = []
# for team in teams:
#     if teams[team]["average_rank"] != 0:
#         rateable_teams.append(team)
#
# print(rate_teams(teams_isr))
