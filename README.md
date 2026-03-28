-Football Passing Network Analysis

Diploma thesis project- structural analysis of football passing networks using network science and data analytics methods.

-Description:
This tool imports real match data from StatsBomb, builds passing networks, computes graph metrics and visualizes them interactively on a football pitch.

-Algorithms Implemented:
a. Degree Centrality
b. Betweenness Centrality
c. PageRank

-Installation:

1. Clone the repository
    git clone https://github.com/xgherix/football-network-analysis.git
    cd football-network-analysis

2. Create virtual environment
    python -m venv .venv
    .venv\Scripts\activate

3. Install dependencies
    pip install -requirements.txt

4. Run the dashboard
    streamlit run app.py

-Project structure:
football-network-analysis/
├── src/
│   ├── data_loader.py       
│   ├── network_builder.py   
│   ├── metrics.py           
│   ├── visualizer.py        
│   └── comparator.py        
├── data/                    
├── notebooks/               
├── outputs/                 
├── app.py                   
└── requirements.txt 

-Technologies:
Python 3.14
NetworkX
Pandas
Plotly
mplsoccer
Streamlit
StatsBombPy