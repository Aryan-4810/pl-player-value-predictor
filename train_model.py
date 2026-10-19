import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

df = pd.read_csv("model_data.csv")

# --- Features ---
features = ["goals", "assists", "minutes_played", "age",
            "points", "goal_diff", "position"]
X = pd.get_dummies(df[features], columns=["position"], drop_first=True)
X["season"] = df["season"]
y = df["log_value"]

# --- 1. Random split (sirf comparison ke liye) ---
X_tr0, X_te0, y_tr0, y_te0 = train_test_split(X, y, test_size=0.2, random_state=42)
lin0 = LinearRegression().fit(X_tr0, y_tr0)
print("Random split  Linear R2:", r2_score(y_te0, lin0.predict(X_te0)))

# --- 2. Honest split: 2012-2022 train, 2023-2025 test ---
train = df["season"] <= 2022
test = df["season"] >= 2023
X_tr, X_te = X[train], X[test]
y_tr, y_te = y[train], y[test]

lin = LinearRegression().fit(X_tr, y_tr)
rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1).fit(X_tr, y_tr)

for name, mdl in [("Linear", lin), ("Forest", rf)]:
    p = mdl.predict(X_te)
    print(f"{name:7s} R2: {r2_score(y_te, p):.3f} | "
          f"MAE(log): {mean_absolute_error(y_te, p):.3f} | "
          f"MAE(EUR): {mean_absolute_error(np.exp(y_te), np.exp(p)):,.0f}")

print("\nLinear coefficients:")
print(pd.Series(lin.coef_, index=X.columns).sort_values())
print("\nForest feature importance:")
print(pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False))

# --- 3. Predicted vs actual (Forest, honest test set) ---
p = rf.predict(X_te)
plt.scatter(y_te, p, alpha=0.3)
lims = [y_te.min(), y_te.max()]
plt.plot(lims, lims, "r--")
plt.xlabel("Actual log value")
plt.ylabel("Predicted log value")
plt.title("Forest, 2023-2025 test set")
plt.savefig("pred_vs_actual.png")
# plt.show()   # window nahi kholni to ye line band rehne do

# --- 4. Models save (website ke liye) ---
joblib.dump(lin, "linear_model.joblib")
joblib.dump(rf, "forest_model.joblib")
joblib.dump(list(X.columns), "feature_columns.joblib")
print("\nsaved models")