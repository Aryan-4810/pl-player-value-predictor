import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("model_data.csv")
features = ["goals", "assists", "minutes_played", "age",
            "points", "goal_diff", "position"]
X = pd.get_dummies(df[features], columns=["position"], drop_first=True)
X["season"] = df["season"]
y = df["log_value"]

rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1).fit(X, y)
joblib.dump(rf, "final_forest.joblib", compress=3)
joblib.dump(list(X.columns), "feature_columns.joblib")
print("saved", X.shape)