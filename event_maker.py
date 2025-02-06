import random
import requests
import os
import warnings
import time

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from ai_predictor import predict_match, predict_matches_scores, predict_matches

AUTH_KEY = "zTmnnKUveaky77Kgv3waDEu6VPrqsMVKcpglKg2so4eey7UEv9uJFfuxGg54rvOj"

teams = requests.get(f'https://www.thebluealliance.com/api/v3/event/2025isde2/teams/keys',
                     headers={"X-TBA-Auth-Key": AUTH_KEY}).json()


def remove_array_from_list(lst, sub_array):
    try:
        lst.remove(sub_array)
    except ValueError:
        pass
    return lst


def generate_matches(teams):
    random.shuffle(teams)
    teams_to_roll = list(teams)
    generated_matches = []
    for i in range(len(teams) * 2):
        random.shuffle(teams_to_roll)
        if len(teams_to_roll) < 6:
            random.shuffle(teams)
            temp_teams_to_roll = [team for team in teams if team not in teams_to_roll]
            reroll_teams = temp_teams_to_roll[:6 - len(teams_to_roll)]
            teams_to_roll += reroll_teams
            generated_matches.append([teams_to_roll[:3], teams_to_roll[3:]])
            teams_to_roll = [team for team in teams if team not in reroll_teams]
        else:
            generated_matches.append([teams_to_roll[:3], teams_to_roll[3:6]])
            teams_to_roll = teams_to_roll[6:]
    return generated_matches


def print_matches_predictions(predicted_match_results):
    for i in range(len(predicted_match_results)):
        print(f'red: {matches[i][0]} blue: {matches[i][1]} \n'
              f'predicted winner: {"red" if predicted_match_results[i][0] > predicted_match_results[i][1] else "blue"} \n'
              f'chance: {max(predicted_match_results[i][0], predicted_match_results[i][1])} \n'
              f'red cage RP chance: {predicted_match_results[i][2]} \n'
              f'red coral RP chance: {predicted_match_results[i][3]} \n'
              f'red auto RP chance: {predicted_match_results[i][4]} \n'
              f'blue cage RP chance: {predicted_match_results[i][5]} \n'
              f'blue coral RP chance: {predicted_match_results[i][6]} \n'
              f'blue auto RP chance: {predicted_match_results[i][7]} \n')


def sort_dict_with_indices(my_dict):
    sorted_items = sorted(my_dict.items(), key=lambda item: item[1])
    indexed_dict = {key: index for index, (key, value) in enumerate(sorted_items)}
    return indexed_dict


matches = []
for i in range(1000):
    matches += generate_matches(teams)
teams_event_rp = {team: 0 for team in teams}
teams_rp_average = {team: 0 for team in teams}
teams_rank_list = {team: [] for team in teams}

start = time.time()
predicted_match_results = predict_matches(matches)

number_of_matches = len(teams) * 2

for i in range(len(predicted_match_results)):
    if i % number_of_matches == 0:
        teams_event_rp = sorted(teams_event_rp.items(), key=lambda item: item[1], reverse=True)
        teams_event_rp = {key: index for index, (key, value) in enumerate(teams_event_rp)}

        for team in teams_event_rp:
            teams_rank_list[team].append(teams_event_rp[team] + 1)
        teams_event_rp = {team: 0 for team in teams}

    red_alliance, blue_alliance = matches[i]
    if predicted_match_results[i][0] > random.random():
        for team in red_alliance:
            teams_event_rp[team] += 3
            teams_rp_average[team] += 3
    else:
        for team in blue_alliance:
            teams_event_rp[team] += 3
            teams_rp_average[team] += 3
    for rp in predicted_match_results[i][2:5]:
        for team in red_alliance:
            if rp > random.random():
                teams_event_rp[team] += 1
                teams_rp_average[team] += 1
    for rp in predicted_match_results[i][5:9]:
        for team in blue_alliance:
            if rp > random.random():
                teams_event_rp[team] += 1
                teams_rp_average[team] += 1

for team in teams_rp_average:
    teams_rp_average[team] /= 1000

teams_rp_average = dict(sorted(teams_rp_average.items(), key=lambda item: item[1], reverse=True))
print(teams_rp_average)

teams_average_rank = {team: 0.0 for team in teams}
for team in teams_rank_list:
    teams_average_rank[team] = sum(teams_rank_list[team]) / 1000
teams_average_rank = dict(sorted(teams_average_rank.items(), key=lambda item: item[1]))
print(teams_average_rank)

for team in teams_rank_list:
    teams_rank_list[team] = sorted(teams_rank_list[team])

teams_top_rank = {team: 0.0 for team in teams}
for team in teams_rank_list:
    teams_top_rank[team] = teams_rank_list[team][100]
teams_top_rank = dict(sorted(teams_top_rank.items(), key=lambda item: item[1]))
print(teams_top_rank)

teams_bottom_rank = {team: 0.0 for team in teams}
for team in teams_rank_list:
    teams_bottom_rank[team] = teams_rank_list[team][950]
teams_bottom_rank = dict(sorted(teams_bottom_rank.items(), key=lambda item: item[1]))
print(teams_bottom_rank)

teams_median_rank = {team: 0.0 for team in teams}
for team in teams_rank_list:
    teams_median_rank[team] = teams_rank_list[team][500]
teams_median_rank = dict(sorted(teams_median_rank.items(), key=lambda item: item[1]))
print(teams_median_rank)
print(len(teams))
end = time.time()
print(end - start)
