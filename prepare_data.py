import pandas as pd
import numpy as np

# --- 1. Appearances (NEW: player_club_id added) ---
app = pd.read_csv(
    "appearances.csv",
    usecols=["player_id", "player_club_id", "date", "competition_id",
             "goals", "assists", "minutes_played"],              # NEW
    parse_dates=["date"],
)
app = app[app["competition_id"] == "GB1"].copy()

app["season"] = app["date"].dt.year.where(app["date"].dt.month >= 8, app["date"].dt.year - 1)

# --- 2. Per player-season totals (NEW: also the club they played most for) ---
stats = app.groupby(["player_id", "season"], as_index=False).agg(     # NEW
    goals=("goals", "sum"),
    assists=("assists", "sum"),
    minutes_played=("minutes_played", "sum"),
    club_id=("player_club_id", lambda s: s.mode().iloc[0]),
)
print(stats.shape)
print(stats.head())

# --- 3. NEW: club strength (points, goal difference) from games.csv ---
games = pd.read_csv(
    "games.csv",
    usecols=["competition_id", "date", "home_club_id", "away_club_id",
             "home_club_goals", "away_club_goals"],
    parse_dates=["date"],
)
games = games[games["competition_id"] == "GB1"].copy()
games["season"] = games["date"].dt.year.where(
    games["date"].dt.month >= 8, games["date"].dt.year - 1)

home = games.rename(columns={"home_club_id": "club_id",
                             "home_club_goals": "gf", "away_club_goals": "ga"})
away = games.rename(columns={"away_club_id": "club_id",
                             "away_club_goals": "gf", "home_club_goals": "ga"})
m = pd.concat([home[["season", "club_id", "gf", "ga"]],
               away[["season", "club_id", "gf", "ga"]]])
m["pts"] = np.where(m["gf"] > m["ga"], 3, np.where(m["gf"] == m["ga"], 1, 0))

club = m.groupby(["season", "club_id"], as_index=False).agg(
    points=("pts", "sum"), gf=("gf", "sum"), ga=("ga", "sum"))
club["goal_diff"] = club["gf"] - club["ga"]

stats = stats.merge(club[["season", "club_id", "points", "goal_diff"]],
                    on=["season", "club_id"], how="left")
print("club merge nulls:", stats["points"].isna().sum())

# --- 4. Valuations (same as before) ---
val = pd.read_csv("player_valuations.csv", parse_dates=["date"])
val = val[["player_id", "date", "market_value_in_eur"]].sort_values("date")

stats["season_end"] = pd.to_datetime((stats["season"] + 1).astype(str) + "-06-30")
stats = stats.sort_values("season_end")

df = pd.merge_asof(
    stats, val,
    left_on="season_end", right_on="date",
    by="player_id", direction="backward",
    tolerance=pd.Timedelta(days=365),
)

players = pd.read_csv("players.csv", usecols=["player_id", "position", "date_of_birth"],
                      parse_dates=["date_of_birth"])
df = df.merge(players, on="player_id", how="left")

df["age"] = (df["season_end"] - df["date_of_birth"]).dt.days / 365.25

# NEW: "points" added to dropna
df = df.dropna(subset=["market_value_in_eur", "age", "position", "points"])
df = df[df["minutes_played"] >= 450]
df["log_value"] = np.log(df["market_value_in_eur"])

print(df.shape)
print(df.isna().sum())
print(df[["goals", "assists", "minutes_played", "age", "points", "goal_diff",
          "market_value_in_eur"]].describe())
df.to_csv("model_data.csv", index=False)