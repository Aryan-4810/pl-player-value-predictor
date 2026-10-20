import streamlit as st
from predict import predict_value

st.set_page_config(page_title="PL Player Value Predictor", page_icon="⚽")

st.title("⚽ Premier League Player Value Predictor")
st.write(
    "Estimate a player's Transfermarkt market value from season stats and "
    "club strength. Model: Random Forest trained on 2012-2025 Premier League data."
)

col1, col2 = st.columns(2)

with col1:
    position = st.selectbox("Position", ["Attack", "Midfield", "Defender", "Goalkeeper"])
    age = st.slider("Age", 17, 40, 25)
    goals = st.number_input("Goals in the season", 0, 40, 5)
    assists = st.number_input("Assists in the season", 0, 25, 3)

with col2:
    minutes = st.slider("Minutes played", 450, 3420, 1800, step=30)
    points = st.slider("Club league points", 10, 100, 55)
    goal_diff = st.slider("Club goal difference", -70, 80, 0)
    season = st.slider("Season (start year)", 2012, 2025, 2025)

if st.button("Predict value", type="primary"):
    value = predict_value(goals, assists, minutes, age, points, goal_diff,
                          position, season)
    st.metric("Estimated market value", f"€{value / 1e6:,.1f}M")
    st.caption(
        "This is an estimate. The model's typical error is about 1.5x "
        "(test R² = 0.75 on 2023-2025 data). It does not know reputation, "
        "nationality or injuries."
    )