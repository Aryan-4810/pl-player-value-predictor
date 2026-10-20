# Premier League Player Market Value Predictor

Predicts a Premier League player's Transfermarkt market value from season
stats and club strength.

## Data
- Transfermarkt dataset on Kaggle ("Football Data from Transfermarkt" by David Cariboo):
  appearances, player_valuations, players, games
- Premier League only, seasons 2012/13 - 2025/26
- 5,525 player-seasons (players with at least 450 minutes)
- CSV files are not in this repo. Download them from Kaggle into the project folder.

## Pipeline
1. `prepare_data.py`: aggregates appearances per player-season, adds club points
   and goal difference from match results, attaches the latest market value at
   season end, computes age, saves `model_data.csv`.
2. `train_model.py`: trains Linear Regression and Random Forest on log(market value),
   evaluates on a time-based split (train 2012-2022, test 2023-2025).
3. `final_train.py`: retrains the Random Forest on all data and saves it.
4. `predict.py`: `predict_value(...)` returns an estimated value in EUR.

## Results (test set: 2023-2025)
| Model | R2 | MAE (log) |
|---|---|---|
| Linear Regression | 0.64 | 0.47 |
| Random Forest | 0.75 | 0.41 |

How the score improved:
- Stats only (goals, assists, minutes, age, position): R2 0.19 on a time-based split.
- Added `season`, because market values inflated about 4x between 2012 and 2025: R2 0.47 (linear), 0.59 (forest).
- Added club strength (season points and goal difference): R2 0.64 (linear), 0.75 (forest).

A random split gave an inflated score at first. A time-based split gives an honest estimate.

## Limitations
- The model does not know reputation, nationality, injuries or potential.
- Club features come from season-end results, so this estimates value after a season, not before a transfer.
- `season` is a feature, so the model is not reliable for seasons far beyond 2025.
- Typical error is about 1.5x the true value (MAE 0.41 on the log scale).
- Residual analysis on the 2023-25 test set shows the model underestimates players whose value is driven by potential or reputation (young prospects
  such as Isak and Estêvão, ageing stars such as Son and van Dijk), and overestimates some low-value squad players.
- Predictions are biased low overall (roughly 10-20%) on the test seasons, likely because market values kept inflating beyond the training range.

## Run
    pip install -r requirements.txt
    python prepare_data.py
    python train_model.py
    python final_train.py
    python predict.py
