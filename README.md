# 🏀 NBA Draft Combine Intelligence

**[Dashboard]([url](https://nbacombinerapmanalysis.streamlit.app/))**

An end-to-end machine learning project exploring whether pre-draft physical measurements predict NBA career success — and why the answer is more complicated than it looks.

---

## The Question

Every June before the NBA draft, prospects look to surprise NBA front offices out with their measurables and athletic abilities. They are made to run sprints, jump, and get standardized measurements at the NBA Draft Combine in Chicago. A common trop among NBA draft fans and scouts is that certain measurables directly correlate to NBA long-term success. Teams are constantly searching for players with large, positive wingspans, large hand sizes and other measurables that they believe directly correlate to success.

This project tries to determine whether this has any merit for a position. Prospects are separated by position group (Guards / Wings / Bigs), using career on-court impact as the outcome variable.

---

## The Catch: A Participation Problem

While in theory, this data should be very helpful for its intended purposes, the truth of it is, that until the NBA enforced that *all* players participate in the 2023 draft cycle, participation was voluntary.

**What this means**

Top prospects routinely skipped the combine. Knowing they were already highly touted and prized in the eyes of scout, a player projected to go in the top 5 had no incentive to risk injury or reveal physical limitations — so they didn't show up. This creates a severe selection bias in the data: the combine data is systematically missing the players who matter most for building a predictive model.

On the other hand, the players who *did* attend were largely borderline prospects, who were told for any chance at moving up the draft board and securing a more guaranteed spot, they had to participate. The result is quite self explanatory:

- The combine sample skews heavily toward players who had modest or short NBA careers
- Elite players (the ones that would show a combine → career success relationship most clearly) are disproportionately absent
- Any model trained on this data will likely underestimate the predictive value of combine measurements under ideal conditions

**The NBA only mandated combine participation starting in 2023**, meaning there are currently fewer than two full draft classes of data where attendance is truly universal. The signal-to-noise ratio should meaningfully improve as those players build out their careers and as more draft classes come in with their complete classes measured accurately.

**Certain prospects train for the Combine**

Another stipulation to consider is that while the nba tries to measure raw athletic abilities, prospects often train for specific drills. The shuttle drill, for example, is notoriously deceptive in that those who perform best have often trained and practiced that exact motion while others rely on their raw physical abilities.
There are many other stories of prospects fudging the numbers, whether it be shortening their standing reach to increase their vertical leap or even not taking the drills seriously.

All of these limitation are baked into the analysis and are worth keeping in mind when reading the R² values on the Key Insights page.

---

## Data Sources

| Source | Description |
|---|---|
| [NBA Draft Combine (Kaggle)](https://www.kaggle.com/datasets/marcusfern/nba-draft-combine) | Physical measurements and athletic testing (2000–2025 draft classes) |
| [Historical NBA Player Box Scores (Kaggle)](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) | Per-game statistics and player info for all regular season games |

**Target variable:** Career average +/− per 36 minutes (mean-centred by position group). This is a raw team +/− measure, not a fully adjusted RAPM, so players who spent careers on strong teams will be slightly inflated. It is used here as a practical proxy in the absence of freely available historical RAPM data.

---

## Combine Features Used

| Feature | Description |
|---|---|
| `HGT` | Height without shoes (inches) |
| `WGT` | Weight (lbs) |
| `BMI` | Body mass index |
| `WNGSPN` | Wingspan (inches) |
| `STNDRCH` | Standing reach (inches) |
| `HANDL` / `HANDW` | Hand length / width (inches) |
| `STNDVERT` | Standing vertical leap (inches) |
| `LPVERT` | Max vertical leap (inches) |
| `LANE` | Lane agility drill time (seconds) |
| `SHUTTLE` | Shuttle run time (seconds) |
| `SPRINT` | ¾-court sprint time (seconds) |
| `BENCH` | Bench press repetitions (185 lbs) |
| `wingspan_diff` | Wingspan − Height (arm length proxy) |
| `reach_diff` | Standing reach − Height (arm length proxy) |
| `vert_diff` | Max vertical − Standing vertical (explosive power proxy) |

---

## Methodology

### Pipeline

```
Kaggle data → merge on player name → career +/− computation
→ combine feature cleaning → position grouping
→ 3 ML models × 3 position groups → feature importance
→ Streamlit dashboard
```

### Models

Three regression models are trained per position group (Guard / Wing / Big) and evaluated with 5-fold cross-validation:

- **Ridge Regression** — linear baseline with L2 regularisation
- **Random Forest** — captures non-linear effects and feature interactions; used for permutation importance
- **Gradient Boosting** — sequential error-correction, typically highest accuracy

Feature importance is measured via Random Forest **permutation importance** (how much does R² drop when each feature is randomly shuffled?) rather than impurity-based importance, which is less reliable for features with different scales.

### Position Grouping

| Group | Positions |
|---|---|
| Guard | PG, SG, G |
| Wing | SF, F, SF-PF, PF-SF |
| Big | PF, C, C-PF, PF-C, F-C |

---

## Dashboard

The Streamlit dashboard has three pages:

**Key Insights** — Scatter plot of composite combine score vs career impact, with players categorised as Blueprint Stars (high combine → top career), Combine Misses (elite measurables, underperformed), Hidden Gems (modest combine, overperformed), or Average. Filterable by position group.
<img width="1736" height="962" alt="image" src="https://github.com/user-attachments/assets/59bb4780-3f01-44e8-9e36-f41631caba6d" />

**Feature Importance** — Bar charts showing which combine metrics have the strongest predictive relationship with career success, per position group.
<img width="1602" height="748" alt="image" src="https://github.com/user-attachments/assets/39fb1fe6-9d09-4fef-8253-916b82807525" />

**Player Lookup** — Search any player in the dataset by last name. Shows their career +/− hero stat, combine measurements vs position average (with green/red text matching their deviation direction) and a deviation bar chart.
<img width="1615" height="957" alt="image" src="https://github.com/user-attachments/assets/c76f20f6-a161-4372-8f81-7c11325c7234" />

### Running Locally

```bash
git clone https://github.com/YOUR_USERNAME/nba-combine-intelligence
cd nba-combine-intelligence

# Install dependencies
pip install -r requirements.txt

# Generate the data (requires Kaggle API credentials)
jupyter nbconvert --to notebook --execute nba_combine_analysis.ipynb

# Launch the dashboard
cd dashboard
streamlit run app.py
```

> **Kaggle credentials:** You'll need a `kaggle.json` API token in `~/.kaggle/` to download the datasets. Get one at [kaggle.com/account](https://www.kaggle.com/account).

---

## Key Findings

A few patterns worth noting, with the caveats in mind:

- **R² values are low across all position groups** (typically −0.05 to +0.15). This is expected given the selection bias — the combine sample is not representative of the full talent distribution.
- **Physical measurements show stronger signal than athletic testing** for most position groups, suggesting that body profile (wingspan relative to height, hand size) carries more information than drill performance.
- **Bigs show the weakest predictability** — unsurprising, since skill, feel and defense are harder to capture at the combine for big men, and because dominant college big men are most likely to skip.
- **Lane agility is consistently among the top features** for guards and wings, suggesting quickness measurements carry real signal even in a biased sample.

These findings should be revisited as post-2023 (mandatory participation) cohorts mature and build out career data.

---

## Project Structure

```
nba-combine-intelligence/
├── nba_combine_analysis.ipynb   # Full data pipeline and ML training
├── requirements.txt
├── dashboard/
│   ├── app.py                   # Streamlit dashboard
│   ├── .streamlit/
│   │   └── config.toml          # Theme configuration
│   └── data/                    # Generated by notebook (not tracked in git)
│       ├── combine_rapm.csv
│       ├── model_summary.csv
│       ├── importance_guard.csv
│       ├── importance_wing.csv
│       ├── importance_big.csv
│       ├── feature_labels.json
│       └── boxscore_per36.csv
└── README.md
```

> The `dashboard/data/` folder is generated by running the notebook and is not committed to the repository.

---

## Limitations & Future Work

- **Selection bias** is the dominant limitation — addressed above
- **Raw +/− as target** is not teammate/opponent adjusted; true RAPM would produce cleaner results
- **Name-matching joins** between datasets drop players with name inconsistencies (accents, suffixes, different spellings)
- **Small sample per position group** after all filtering (~150–400 players per group) limits the power of the ML models
- **Future:** as mandatory combine data accumulates post-2023, re-running this analysis on that cohort alone would give a much cleaner test of whether combine measurements actually predict career success

---

## Built With

Python · Pandas · scikit-learn · Plotly · Streamlit · Kaggle datasets

---

*Built by [Joshua Hey](https://www.linkedin.com/in/joshua-hey-214173279/) · Systems Design Engineering, University of Waterloo*
