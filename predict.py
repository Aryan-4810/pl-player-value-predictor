import numpy as np
import pandas as pd
import joblib

model = joblib.load("final_forest.joblib")
cols = joblib.load("feature_columns.joblib")


def predict_value(goals, assists, minutes, age, points, goal_diff,
                  position, season=2025):
    """Return predicted market value in EUR.

    position must be one of: "Attack", "Midfield", "Defender", "Goalkeeper"
    """
    row = pd.DataFrame([{
        "goals": goals,
        "assists": assists,
        "minutes_played": minutes,
        "age": age,
        "points": points,
        "goal_diff": goal_diff,
        "season": season,
        "position": position,
    }])
    row = pd.get_dummies(row, columns=["position"])
    row = row.reindex(columns=cols, fill_value=0)  # missing dummy columns = 0
    return float(np.exp(model.predict(row)[0]))


if __name__ == "__main__":
    print(predict_value(20, 8, 2800, 25, 80, 40, "Attack"))    # star attacker
    print(predict_value(1, 0, 900, 33, 40, -15, "Defender"))   # old bench defender
    print(predict_value(20, 8, 2800, 33, 80, 40, "Attack"))    # same, age 33