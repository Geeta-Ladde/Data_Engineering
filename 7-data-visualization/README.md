# 📊 Halo 5 Gaming Analytics — Tableau Data Visualization

> **Two interactive Tableau Public dashboards analyzing Halo 5 multiplayer
> game data across 50,000+ match records — an executive summary view and
> an exploratory drill-down dashboard with dynamic filters.**

---

## 📌 Project Summary

This project transforms raw Halo 5 gaming data into interactive business
intelligence dashboards using Tableau Public. The data was pre-processed
and aggregated using PySpark before visualization — demonstrating the
full data engineering to analytics pipeline.

**The business questions answered:**
> - *"What are the overall trends in daily player activity and match volume?"*
> - *"Which medals are awarded most frequently and across which game modes?"*
> - *"Who are the top performing players by total medals and match participation?"*
> - *"How does activity vary by day of week, month, and game map?"*

---

## 🔗 Live Dashboards

| Dashboard | Description | Link |
|-----------|-------------|------|
| 🎯 Executive Dashboard | High-level KPIs and trends | [View Dashboard](https://public.tableau.com/app/profile/geeta.ladde/viz/Halo_Executive_Dashboard/Dashboard1?publish=yes) |
| 🔍 Exploratory Dashboard | Interactive filters for deep-dive analysis | [View Dashboard](https://public.tableau.com/app/profile/geeta.ladde/viz/Book1_17637733241420/ExploratoryDashboard?publish=yes) |

---

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    END-TO-END PIPELINE                      │
│                                                             │
│  RAW DATA              PROCESSING           VISUALIZATION   │
│                                                             │
│  match_details.csv  →  PySpark ETL      →  Executive       │
│  matches.csv           Aggregation          Dashboard       │
│  medals.csv            & Cleaning                          │
│  medals_matches        ↓                →  Exploratory     │
│  _players.csv       daily_activity         Dashboard       │
│                     _clean.csv                             │
│                     medal_summary                          │
│                     _clean.csv                             │
│                     player_summary                         │
│                     _clean.csv                             │
│                     halo_sample_50k                        │
│                     .csv                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
06_data_visualization/
│
├── README.md
├── tableau_links.txt              ← Direct links to live dashboards
│
└── data/
    ├── daily_activity_clean.csv   ← Daily match + player + medal counts
    ├── medal_summary_clean.csv    ← Medal types, difficulty, award counts
    ├── player_summary_clean.csv   ← Player performance aggregates
    └── halo_sample_50k.csv        ← 50K sampled match records for Tableau
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| **Tableau Public** | Interactive dashboard creation |
| **PySpark** | Data preprocessing and aggregation |
| **Python / Pandas** | Data cleaning and sampling |
| **Halo 5 Dataset** | Source gaming data |

---

## 📊 Dashboard Details

### 🎯 Executive Dashboard
**Purpose:** High-level overview for stakeholders who need quick insights

**Key Visualizations:**
- Daily active players and match volume trend line
- Total medals awarded by medal classification
- Top performing players by total medals
- Monthly activity heatmap

**Design Principles:**
- Minimal filters — designed for at-a-glance consumption
- KPI tiles showing overall totals
- Clean color scheme with consistent branding

---

### 🔍 Exploratory Dashboard
**Purpose:** Deep-dive analysis with dynamic filters for analysts

**Key Visualizations:**
- Medal distribution by classification and difficulty
- Player performance breakdown by map and game mode
- Day-of-week activity patterns
- Medal awards over time with drill-down capability

**Interactive Features:**
- Filter by medal classification
- Filter by map
- Filter by date range
- Filter by game mode
- Cross-filtering between charts

---

## 📈 Dataset Overview

### daily_activity_clean.csv
| Column | Description |
|--------|-------------|
| Date | Match date |
| Month | Year-month grouping |
| Matches | Total matches played |
| Active_Players | Unique players active |
| Total_Medals | Total medals awarded |

### medal_summary_clean.csv
| Column | Description |
|--------|-------------|
| Medal_Name | Name of the medal |
| Classification | Category (KillingSpree, Vehicles, etc.) |
| Difficulty | Difficulty score (0-100) |
| Total_Awards | Times awarded total |
| Unique_Players | Distinct players who earned it |

### player_summary_clean.csv
| Column | Description |
|--------|-------------|
| Player | Player gamertag |
| Matches_Played | Total matches participated in |
| Total_Medals | All-time medal count |
| Unique_Medals | Distinct medal types earned |
| Avg_Medals_Per_Match | Engagement efficiency metric |

### halo_sample_50k.csv
50,000 sampled records from the full match dataset including:
match_id, player_gamertag, medal details, map, game mode,
completion date, and time dimensions (year, month, day_of_week)

---

## 💼 Real-World Applications

This dashboard design pattern is used across industries:

| Industry | Executive Dashboard | Exploratory Dashboard |
|----------|--------------------|-----------------------|
| 🎮 Gaming | DAU/MAU trends | Player behavior analysis |
| 🛒 E-commerce | Revenue KPIs | Product performance drill-down |
| 📱 SaaS | Churn/retention | Feature usage exploration |
| 🏥 Healthcare | Patient volume | Treatment outcome analysis |

---

## 🎓 About This Project

This project demonstrates the full analytics engineering pipeline —
from raw event data through distributed PySpark processing to
interactive business intelligence dashboards — applied to Halo 5
multiplayer gaming data.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [Tableau Public Gallery](https://public.tableau.com/app/profile/geeta.ladde)
- [Tableau Dashboard Best Practices](https://www.tableau.com/learn/articles/best-practices-for-effective-dashboards)

---

⭐ **If this helped you understand data visualization patterns, please give it a star!**
