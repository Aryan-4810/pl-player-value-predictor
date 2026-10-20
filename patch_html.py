"""Patches templates/index.html (the Stitch export):
 1. replaces the fake JavaScript valuation formula with a call to /predict
 2. replaces invented claims with facts from the real project
Run once:  python patch_html.py
"""
import re

PATH = "templates/index.html"
html = open(PATH, encoding="utf-8").read()


def rep(old, new):
    global html
    n = html.count(old)
    if n != 1:
        raise SystemExit(f"Expected exactly 1 match, found {n} for:\n  {old[:80]}")
    html = html.replace(old, new)


# ---------- 1. Real model instead of the fake JS formula ----------
NEW_JS = """    let predictTimer = null;

    function recalculateValuation() {
      clearTimeout(predictTimer);
      predictTimer = setTimeout(fetchPrediction, 250);
    }

    async function fetchPrediction() {
      const valEl = document.getElementById('valuationValue');
      const payload = {
        position: currentPosition,
        age: parseInt(document.getElementById('ageInput').value, 10),
        goals: parseInt(document.getElementById('goalsVal').innerText, 10),
        assists: parseInt(document.getElementById('assistsVal').innerText, 10),
        minutes: parseInt(document.getElementById('minsInput').value, 10),
        points: parseInt(document.getElementById('ptsInput').value, 10),
        goal_diff: parseInt(document.getElementById('gdInput').value, 10),
        season: parseInt(document.getElementById('seasonInput').value, 10)
      };
      try {
        const res = await fetch('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Request failed');

        const m = v => (v / 1e6).toFixed(1);
        valEl.innerText = `\\u20ac${m(data.value_eur)}M`;
        document.getElementById('rangeBadge').innerHTML =
          `Typical range: <span class="text-primary-fixed-dim">\\u20ac${m(data.low_eur)}M</span> \\u2013 <span class="text-secondary-fixed-dim">\\u20ac${m(data.high_eur)}M</span>`;

        const v = data.value_eur / 1e6;
        const tierEl = document.getElementById('tierDisplay');
        if (v >= 60) tierEl.innerText = 'Very high value tier';
        else if (v >= 38) tierEl.innerText = 'High value tier';
        else if (v >= 20) tierEl.innerText = 'Established starter tier';
        else tierEl.innerText = 'Squad / rotation tier';
      } catch (err) {
        valEl.innerText = 'Error';
        document.getElementById('tierDisplay').innerText = String(err.message || err);
      }
    }

"""
html, n = re.subn(
        r"[ \t]*function recalculateValuation\(\) \{.*?(?=[ \t]*function runPredictionAnimation\(\))",
    lambda m: NEW_JS,
    html,
    flags=re.DOTALL,
)
if n != 1:
    raise SystemExit("Could not find recalculateValuation() block")

# ---------- 2. Remove the invented feature-contribution block ----------
html, n = re.subn(
    r"<!-- Feature Impact Breakdown Tags -->.*?(?=<!-- Small Note Error Profile -->)",
    "",
    html,
    flags=re.DOTALL,
)
if n != 1:
    raise SystemExit("Could not find feature contribution block")

# ---------- 3. Replace invented claims with real ones ----------
rep("ML MODEL v2.4", "RANDOM FOREST")
rep("Machine Learning Market Valuation for Premier League Players trained on historical transfer amortizations &amp; tactical metrics.",
    "Estimates a Premier League player's Transfermarkt market value from season stats and club strength. Trained on 2012-2025 data.")
rep("N=1,420 Seasons", "N=5,525 Player-Seasons")
rep("R² 0.75 Telemetry", "R² 0.75 (2023-25 test)")
rep("CONFIDENCE: 92%", "TEST R² 0.75")
rep("94th PCTL", "MODEL OUTPUT")
rep("FINANCIAL SEASON BASE", "SEASON")
rep("€48.5M", "...")
rep("€32.3M", "...")
rep("€72.8M", "...")
rep("Estimate. Typical error about 1.5x. Random Forest, R² 0.75 on 2023-2025 test data. Market volatility may influence final contractual buyout clauses.",
    "Estimate. Typical error about 1.5x (Random Forest, R² 0.75 on 2023-2025 test data). It does not know reputation, potential or injuries.")
rep("Normalizes attacking outputs per 90 (G+A/90), factoring squad strength coefficients, team goal differential, and position-specific age-depreciation curves.",
    "Combines season goals, assists, minutes, age and position with club strength (league points and goal difference) and the season. Data: Transfermarkt, 5,500+ Premier League player-seasons (2012-2025). The target is log market value.")
rep("Utilizes 500 gradient-stabilized decision trees to capture nonlinear valuation thresholds (e.g., Champions League team premiums and breakout goalscorer spikes).",
    "A Random Forest of 200 decision trees captures non-linear effects, such as the premium for playing at a strong club.")
rep("Rigorously back-tested against realized Premier League summer transfer windows between 2023 and 2025 to suppress overfitting and inflation bias.",
    "Trained on seasons 2012-2022 and tested on 2023-2025 (R² 0.75). A time-based split avoids leaking future information. Known weakness: it underestimates young prospects and ageing stars.")
rep('href="https://github.com" rel',
    'href="https://github.com/Aryan-4810/pl-player-value-predictor" rel')
rep("<span>★ 420 STARS</span>", "<span>VIEW ON GITHUB</span>")
rep("<span>OPEN SOURCE MIT</span>", "<span>SCIKIT-LEARN</span>")
rep("<span>PYTHON 3.11</span>", "<span>PYTHON</span>")
rep("© 2025 ValueMetrics Analytics. Institutional sports intelligence platform. R² 0.75 Random Forest Model.",
    "Student project by Aryan. Data: Transfermarkt (Kaggle). Estimates only.")

open(PATH, "w", encoding="utf-8").write(html)
print("Patched OK ->", PATH)