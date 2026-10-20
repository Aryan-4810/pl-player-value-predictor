import os
from flask import Flask, request, jsonify, send_file
from predict import predict_value

app = Flask(__name__)

POSITIONS = {"Attack", "Midfield", "Defender", "Goalkeeper"}

# (min, max) allowed for each numeric input
LIMITS = {
    "goals": (0, 45),
    "assists": (0, 30),
    "minutes": (0, 3420),
    "age": (15, 45),
    "points": (0, 110),
    "goal_diff": (-100, 100),
    "season": (2012, 2026),
}


@app.get("/")
def home():
    return send_file(os.path.join(app.root_path, "templates", "index.html"))


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}

    if data.get("position") not in POSITIONS:
        return jsonify(error="Invalid position"), 400

    values = {}
    for key, (lo, hi) in LIMITS.items():
        try:
            v = float(data[key])
        except (KeyError, TypeError, ValueError):
            return jsonify(error=f"Missing or invalid: {key}"), 400
        if not lo <= v <= hi:
            return jsonify(error=f"{key} must be between {lo} and {hi}"), 400
        values[key] = v

    value = predict_value(
        goals=values["goals"],
        assists=values["assists"],
        minutes=values["minutes"],
        age=values["age"],
        points=values["points"],
        goal_diff=values["goal_diff"],
        position=data["position"],
        season=int(values["season"]),
    )

    # Typical error is about 1.5x (MAE 0.41 on the log scale), so show that range
    return jsonify(
        value_eur=value,
        low_eur=value / 1.5,
        high_eur=value * 1.5,
    )


if __name__ == "__main__":
    app.run(debug=True)