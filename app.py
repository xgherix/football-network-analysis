import streamlit as st
from src.data_loader import get_competitions, get_matches, get_team_passes
from src.network_builder import build_passing_network
from src.metrics import all_metrics
from src.visualizer import draw_passing_network
from src.comparator import compare_teams, compare_summary_df

st.set_page_config(
    page_title="Football Passing Network Analysis",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Passing Network Analysis")
st.markdown("Structural analysis of football passing networks using network science.")

st.sidebar.header("Match Selection")

@st.cache_data
def load_competitions():
    return get_competitions()

@st.cache_data
def load_matches(competition_id, season_id):
    return get_matches(competition_id, season_id)

competitions = load_competitions()
competition_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in competitions.iterrows()
}

selected_comp = st.sidebar.selectbox("Competition", list(competition_options.keys()))
competition_id, season_id = competition_options[selected_comp]

matches = load_matches(competition_id, season_id)
match_options = {
    f"{row['home_team']} vs {row['away_team']} ({row['match_date']})": (
        row["match_id"], row["home_team"], row["away_team"]
    )
    for _, row in matches.iterrows()
}

selected_match = st.sidebar.selectbox("Match", list(match_options.keys()))
match_id, home_team, away_team = match_options[selected_match]

mode = st.sidebar.radio("Mode", ["Single team", "Compare teams"])

st.sidebar.markdown("---")
st.sidebar.caption("Data provided by StatsBomb Open Data")

if mode == "Single team":
    team = st.sidebar.selectbox("Select team", [home_team, away_team])
    flip = team == away_team

    with st.spinner("Loading passing network..."):
        passes = get_team_passes(match_id, team)
        G = build_passing_network(passes)
        fig = draw_passing_network(G, passes, team, flip=flip)
        metrics = all_metrics(G)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Player metrics")
    st.dataframe(
        metrics.style.format({
            "in_degree": "{:.4f}",
            "out_degree": "{:.4f}",
            "total_degree": "{:.4f}",
            "betweenness": "{:.4f}",
            "pagerank": "{:.4f}",
        }),
        use_container_width=True
    )

elif mode == "Compare teams":
    with st.spinner("Loading comparison..."):
        comparison = compare_teams(match_id, home_team, away_team)
        summary_df = compare_summary_df(comparison)

    st.subheader(f"Network comparison: {home_team} vs {away_team}")
    st.dataframe(summary_df, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {home_team}")
        fig1 = draw_passing_network(
            comparison["team1"]["graph"],
            comparison["team1"]["passes"],
            home_team,
            flip=False
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(comparison["team1"]["metrics"].style.format({
            "in_degree": "{:.4f}", "out_degree": "{:.4f}",
            "total_degree": "{:.4f}", "betweenness": "{:.4f}",
            "pagerank": "{:.4f}",
        }), use_container_width=True)

    with col2:
        st.markdown(f"### {away_team}")
        fig2 = draw_passing_network(
            comparison["team2"]["graph"],
            comparison["team2"]["passes"],
            away_team,
            flip=True
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(comparison["team2"]["metrics"].style.format({
            "in_degree": "{:.4f}", "out_degree": "{:.4f}",
            "total_degree": "{:.4f}", "betweenness": "{:.4f}",
            "pagerank": "{:.4f}",
        }), use_container_width=True)