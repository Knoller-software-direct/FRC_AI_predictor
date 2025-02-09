import csv
import json
import requests

from constants import AUTH_KEY
from team_rater import rate_teams




def get_worlds_teams(worlds_keys, year):
    teams_in_worlds = []

    for key in worlds_keys:
        teams_in_worlds += requests.get(f'https://www.thebluealliance.com/api/v3/event/{key}/teams/keys',
                                        headers={"X-TBA-Auth-Key": AUTH_KEY}).json()
    with open(f"worlds_teams_{year}.json", "w") as outfile:
        outfile.write(json.dumps(teams_in_worlds, indent=4))


with open("worlds_teams_2024.json", "r") as file:
    world_teams = json.load(file)


# for team in teams_rating:
#     if not (team in world_teams):
#         print(f'team {team} didnt make it with {teams_rating[team]}')
