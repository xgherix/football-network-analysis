# Football Passing Network Analysis

Diploma thesis project- structural analysis of football passing networks using network science and data analytics methods.

# Live Demo
🌐[diploma.streamlit.app](https://diploma.streamlit.app)

## Description:
This tool imports real data match from StatsBomb, builds passing networks, computes graph metrics and visualizes them intereactively on a football pitch. It automatically generates tactical interpretations readable by anyone - coaches, journalists and fans - not just data scientists.

## Features
- Interactive passing network visualization on a football pitch
- Analysis by period - Full match, First half, Second half,
- Starting XI filter - analyze only the 11 players who started
- Automatic tactical interpretation in plain English
- Team comparison with side-by-side network analysis
- Player role detection - playmaker, bridge, distributor, target

## Algorithms Implemented:
- **Degree Centrality** - measures player involvement in passing
- **Betweenness Centrality** - identifies key bridge players
- **PageRank** - measures tactical influence and prestige
- **Clustering Coefficent** - detects combination play patterns
- **Network Density** - characterizes team playing style

## Installation:

### 1. Clone the repository
```bash
git clone https://github.com/xgherix/football-network-analysis.git
cd football-network-analysis
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

## Project Structure

```
football-network-analysis/
│
├── src/
│   ├── data_loader.py       # StatsBomb data import and filtering
│   ├── network_builder.py   # Graph construction from pass data
│   ├── metrics.py           # Centrality algorithms
│   ├── visualizer.py        # Interactive pitch visualization
│   ├── comparator.py        # Team and match comparison
│   └── interpreter.py       # Automatic tactical interpretation
│
├── data/                    # Local data files
├── notebooks/               # Jupyter exploration notebooks
├── outputs/                 # Saved figures
├── app.py                   # Streamlit dashboard entry point
└── requirements.txt         # Project dependencies
```

## Data Source
All match data is provided by [StatsBomb Open Data](https://github.com/statsbomb/open-data) — free and publicly available for academic and educational use.

## Technologies
- Python 3.11
- NetworkX
- pandas
- Plotly
- mplsoccer
- Streamlit
- StatsBombPy
- scipy

## Author
Algert Kolaveri — Bachelor Thesis
Universiteti Politeknik i Tiranes, Fakulteti i Teknologjise dhe Informacionit