import math

import numpy as np
import json
import os
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

from data_preperations import get_team_features

model = tf.keras.models.load_model("frc_match_predictor_v4.keras")

with open("teams.json", "r") as file:
    teams = json.load(file)


def predict_cage_rp(alliance):
    max_epa = max([teams[alliance[0]]["epa"], teams[alliance[1]]["epa"], teams[alliance[2]]["epa"]])
    return 1 / (1 + math.exp(-(1 / 150) * (max_epa - 1550)))


def predict_coral_rp(alliance):
    sum_epa = sum([teams[alliance[0]]["epa"], teams[alliance[1]]["epa"], teams[alliance[2]]["epa"]])
    return 1 / (1 + math.exp(-(1 / 50) * (sum_epa - 1575 * 3)))


def predict_auto_rp(alliance):
    sum_epa = sum([teams[alliance[0]]["epa"], teams[alliance[1]]["epa"], teams[alliance[2]]["epa"]])
    return 1 / (1 + math.exp(-(1 / 200) * (sum_epa - 1400 * 3)))


def predict_alliance_match_rp(alliance):
    return [predict_cage_rp(alliance), predict_coral_rp(alliance), predict_auto_rp(alliance)]


def predict_matches_scores(matches):
    feature_vectors = []

    for match in matches:
        red_alliance, blue_alliance = match
        try:
            red_features = np.array([get_team_features(t, teams) for t in red_alliance])
            blue_features = np.array([get_team_features(t, teams) for t in blue_alliance])
        except KeyError as e:
            feature_vectors.append(None)
            continue

        red_summary = np.concatenate([red_features.mean(axis=0), red_features.max(axis=0)])
        blue_summary = np.concatenate([blue_features.mean(axis=0), blue_features.max(axis=0)])

        feature_vector = np.concatenate([red_summary, blue_summary]).reshape(1, -1)
        feature_vectors.append(feature_vector)

    feature_vectors = np.vstack([fv for fv in feature_vectors if fv is not None])

    predictions = model.predict(feature_vectors, verbose=0)

    result = []
    for prediction in predictions:
        result.append((prediction[0], 1 - prediction[0]))

    return result


def predict_matches(matches):
    scores = predict_matches_scores(matches)
    predictions = []
    for i in range(len(matches)):
        predictions.append(list(scores[i]) + predict_alliance_match_rp(matches[i][0]) + predict_alliance_match_rp(matches[i][1]))

    return predictions

def predict_match(red_alliance, blue_alliance):
    try:
        red_features = np.array([get_team_features(t, teams) for t in red_alliance])
        blue_features = np.array([get_team_features(t, teams) for t in blue_alliance])
    except KeyError as e:
        return None, 0.5

    red_summary = np.concatenate([red_features.mean(axis=0), red_features.max(axis=0)])
    blue_summary = np.concatenate([blue_features.mean(axis=0), blue_features.max(axis=0)])

    feature_vector = np.concatenate([red_summary, blue_summary]).reshape(1, -1)

    prediction = model.predict(feature_vector, verbose=0)[0][0]
    predicted_winner = "red" if prediction > 0.5 else "blue"
    confidence = prediction if prediction > 0.5 else 1 - prediction

    if predicted_winner is None or confidence is None:
        return None, 0.5
    return predicted_winner, confidence


def test_accuracy(events):
    checkpoints = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

    for event in events:
        for match in events[event]["matches"]:
            try:
                predicted_winner, confidence = predict_match(match["red_alliance"], match["blue_alliance"])
                index = int((confidence - 0.5) * 10)
                checkpoints[index][0] += 1
                if predicted_winner != match["winner"]:
                    checkpoints[index][1] += 1
            except:
                print(match)

    for i in range(len(checkpoints)):
        print(f'prediction of {0.5 + i / 10} was wrong {checkpoints[i][1]}/{checkpoints[i][0]}')
