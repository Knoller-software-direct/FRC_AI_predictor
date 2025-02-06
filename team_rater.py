import json

from ai_predictor import predict_matches_scores


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

    print(team_json)


with open("teams.json", "r") as file:
    teams = json.load(file)

matches = []

rateable_teams = []
for team in teams:
    if teams[team]["average_rank"] != 0:
        rateable_teams.append(team)

teams_scores = {team: 0.0 for team in rateable_teams}

for team in rateable_teams:
    matches.append([[team, team, team], ["average_team", "average_team", "average_team"]])

scores = predict_matches_scores(matches)
for i in range(len(scores)):
    teams_scores[matches[i][0][0]] += float(scores[i][0])

teams_scores = sorted(teams_scores.items(), key=lambda item: item[1], reverse=True)

teams_scores = {key: index + 1 for index, (key, value) in enumerate(teams_scores)}
print(teams_scores)
