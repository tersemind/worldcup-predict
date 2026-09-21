# WorldCup Predict v1.1 (Path B: live-refresh edition)

Real computation + live data = a reproducible World Cup prediction engine.

---

## 🎯 Core architecture (Path B)

```
                  ┌─────────────────────────────┐
                  │  Claude (orchestration)     │
                  │  - WebFetch for Polymarket  │
                  │  - WebSearch for injuries   │
                  │  - parse → call Bash        │
                  └────────────┬────────────────┘
                               │
                  ┌────────────▼────────────────┐
                  │  Python layer (compute/IO)  │
                  │  - refresh_helper.py writes │
                  │  - run_tournament.py predicts│
                  └────────────┬────────────────┘
                               │
                  ┌────────────▼────────────────┐
                  │  Local data layer           │
                  │  - teams.json (48 teams)    │
                  │  - groups.json              │
                  │  - outputs/*.json           │
                  └─────────────────────────────┘
```

**Division of labor**:
- **Live data collection**: Claude (WebFetch/WebSearch)
- **Data persistence**: Python (integrity)
- **Math**: Python (reproducibility)
- **Presentation**: Claude (readability)

---

## 🚀 Usage

### Full flow

```
1. /wc-predict refresh market       → Claude fetches Polymarket → Python writes teams.json
2. /wc-predict tournament 10000     → Python runs Monte Carlo + synthesized prediction
3. /wc-predict match Spain vs France → Python runs a single-match prediction
```

### Subcommands

| Command | Action | Tools |
|---|---|---|
| `/wc-predict tournament [N]` | Monte Carlo + synthesized prediction | Bash → Python |
| `/wc-predict match A vs B` | single-match W/D/L + score probabilities | Bash → Python |
| `/wc-predict refresh` | live-refresh all fields | WebFetch + WebSearch + Bash |
| `/wc-predict refresh elo` | Elo only (eloratings.net) | WebFetch + Bash |
| `/wc-predict refresh market` | market odds only (Polymarket) | WebFetch + Bash |
| `/wc-predict refresh injuries` | injury intel only (ESPN/BBC) | WebSearch + suggestions |
| `/wc-predict update <T> <F> <V>` | manually edit one field | Bash → Python |
| `/wc-predict data` | inspect current data | Bash → Python |

---

## 📊 Test results (after refreshing with live Polymarket data)

Before vs after refresh:

| Team | old market | new market (live) | model prob | new divergence |
|---|---|---|---|---|
| Spain | 18.2% | **17.5%** | 18.6% | +1.1pp |
| France | 16.7% | **16.0%** | 16.9% | +0.9pp |
| Argentina | 11.1% | **9.0%** | 10.6% | **+1.6pp** ⬆️ |
| Portugal | 8.3% | **11.0%** | 6.7% | -4.3pp |
| Brazil | 11.1% | **8.5%** | 5.0% | -3.5pp |

→ Under the new data, Argentina becomes the largest positive-divergence candidate
(the market's confidence in Argentina has slipped)

---

## 📁 Project layout

```
~/.codebuddy/worldcup-predict/
├── README.md                    # this file
├── code/
│   ├── data/
│   │   ├── refresh_helper.py    # data refresh helpers
│   │   └── __init__.py
│   ├── models/
│   │   ├── elo_engine.py        # Elo ratings
│   │   ├── poisson_model.py     # Dixon-Coles
│   │   ├── monte_carlo.py       # Monte Carlo 10k
│   │   └── synthesizer.py       # synthesized prediction (reads latest market)
│   ├── utils/
│   │   └── io.py                # data loading
│   ├── run_tournament.py        # tournament entry point
│   └── predict_match.py         # single-match entry point
├── data/
│   ├── raw/
│   │   ├── teams.json           # 48 teams baseline (with _last_updated timestamps)
│   │   └── groups.json          # 12 groups
│   └── outputs/
│       ├── mc_simulation_n10000.json
│       └── synthesizer_report.json
└── logs/
```

---

## 🔧 Developers: run Python directly

```bash
# Inspect current data
python3 ~/.codebuddy/worldcup-predict/code/data/refresh_helper.py show

# Update one field manually
python3 ~/.codebuddy/worldcup-predict/code/data/refresh_helper.py update Spain elo 2160

# Run the full tournament prediction
python3 ~/.codebuddy/worldcup-predict/code/run_tournament.py 10000

# Run a single match
python3 ~/.codebuddy/worldcup-predict/code/predict_match.py "Spain" "France"

# Re-run only the synthesized prediction (skip Monte Carlo)
python3 ~/.codebuddy/worldcup-predict/code/models/synthesizer.py
```

---

## ⚙️ Data update mechanics

### Field precedence

1. **Manual Edit** > **refresh_helper.py update** > **static teams.json**
2. **synthesizer.py reads `market_implied` with precedence**:
   - First: `teams.json` (latest)
   - Fallback: `mc_simulation_n*.json` (Monte Carlo snapshot)

### Automatic timestamps

Every `update` automatically writes a `_last_updated` field:

```json
"_last_updated": {
  "Spain": {"market_implied": "2026-06-11 16:45:00"},
  "France": {"market_implied": "2026-06-11 16:45:00"}
}
```

---

## 📝 Limitations

1. **Elo auto-fetch not implemented**: only market odds refresh automatically; Elo must be
   fetched manually from eloratings.net
2. **Injuries don't write to the store directly**: `refresh injuries` produces suggestions
   that you apply manually to synthesizer.py
3. **Timezone/altitude/weather not online**: injected as static adjustment factors in the
   synthesizer
4. **ML layer not implemented**: XGBoost is not trained yet (needs a historical-match dataset)

---

## 🆚 The three versions

| Version | Compute | Data | Directory |
|---|---|---|---|
| Prompt v1 (backup) | LLM role-play | in-context memory | `worldcup-predictor-prompt-v1` |
| Prompt v1 (current) | LLM role-play | in-context memory | `worldcup-predictor` |
| **Engine v1 (Path B)** ⭐ | **real numpy/scipy** | **live refresh** | **`worldcup-predict`** |

---

## 🎓 Design philosophy

1. **Static computation in Python**: reproducible, auditable
2. **Dynamic data via Claude**: fresh, with understanding
3. **Persistence in Python**: integrity, traceability
4. **Presentation via Claude**: readability, context

→ The optimal division of labor between "AI + engineering".
