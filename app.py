import streamlit as st
import networkx as nx
from src.data_loader import get_competitions, get_matches, get_team_passes_filtered
from src.network_builder import build_passing_network, get_network_summary
from src.metrics import all_metrics
from src.visualizer import draw_passing_network
from src.comparator import compare_teams, compare_summary_df
from src.interpreter import interpret_match, compare_interpretation

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

analysis_mode = st.sidebar.selectbox(
    "Analysis period",
    [
        "Full match",
        "First half",
        "Second half",
        "Starting XI — Full match",
        "Starting XI — First half",
        "Starting XI — Second half",
    ]
)

period_map = {
    "Full match": (None, False),
    "First half": (1, False),
    "Second half": (2, False),
    "Starting XI — Full match": (None, True),
    "Starting XI — First half": (1, True),
    "Starting XI — Second half": (2, True),
}
period, starting_xi_only = period_map[analysis_mode]

st.sidebar.markdown("---")
st.sidebar.caption("Data provided by StatsBomb Open Data")

if mode == "Single team":
    team = st.sidebar.selectbox("Select team", [home_team, away_team])
    opponent = away_team if team == home_team else home_team
    flip = team == away_team

    with st.spinner("Loading passing network..."):
        passes = get_team_passes_filtered(match_id, team,
                                          period=period,
                                          starting_xi_only=starting_xi_only)
        opponent_passes = get_team_passes_filtered(match_id, opponent,
                                                   period=period,
                                                   starting_xi_only=starting_xi_only)
        G = build_passing_network(passes)
        G_opp = build_passing_network(opponent_passes)
        fig = draw_passing_network(G, passes, f"{team} — {analysis_mode}", flip=flip)
        metrics = all_metrics(G)
        summary = get_network_summary(G)
        clustering = nx.average_clustering(G.to_undirected())

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Match analysis")
    st.caption(f"Period: {analysis_mode}")

    interpretation = interpret_match(
        team=team,
        G=G,
        passes=passes,
        total_passes=summary["total_passes"],
        density=summary["density"],
        clustering=round(clustering, 4),
        opponent=opponent,
        opponent_passes=get_network_summary(G_opp)["total_passes"],
    )
    for line in interpretation.split("\n\n"):
        st.markdown(line)

    st.markdown("---")

    st.subheader("Player roles")
    col1, col2, col3, col4 = st.columns(4)

    top_pagerank = metrics.loc[metrics["pagerank"].idxmax(), "player"]
    top_betweenness = metrics.loc[metrics["betweenness"].idxmax(), "player"]
    top_out = metrics.loc[metrics["out_degree"].idxmax(), "player"]
    top_in = metrics.loc[metrics["in_degree"].idxmax(), "player"]

    col1.metric("Tactical heart", top_pagerank, help="Highest PageRank")
    col2.metric("Key bridge", top_betweenness, help="Highest Betweenness")
    col3.metric("Main distributor", top_out, help="Highest Out-degree")
    col4.metric("Most sought", top_in, help="Highest In-degree")

    st.markdown("---")

    st.subheader("Network statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total passes", summary["total_passes"])
    c2.metric("Passing combinations", summary["passing_combinations"])
    c3.metric("Network density", summary["density"])
    c4.metric("Avg clustering", round(clustering, 4))

    st.markdown("---")

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
        comparison = compare_teams(
            match_id, home_team, away_team,
            period=period,
            starting_xi_only=starting_xi_only
        )
        summary_df = compare_summary_df(comparison)

    st.subheader(f"Match analysis: {home_team} vs {away_team}")
    st.caption(f"Period: {analysis_mode}")

    interpretation = compare_interpretation(comparison)
    for line in interpretation.split("\n\n"):
        st.markdown(line)

    st.markdown("---")

    st.subheader("Network comparison")
    st.dataframe(summary_df, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {home_team}")
        fig1 = draw_passing_network(
            comparison["team1"]["graph"],
            comparison["team1"]["passes"],
            f"{home_team} — {analysis_mode}",
            flip=False
        )
        st.plotly_chart(fig1, use_container_width=True)

        s1 = comparison["team1"]["summary"]
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("Tactical heart", s1["top_pagerank_player"])
        r1c2.metric("Key bridge", s1["top_betweenness_player"])
        r1c3.metric("Total passes", s1["total_passes"])

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
            f"{away_team} — {analysis_mode}",
            flip=True
        )
        st.plotly_chart(fig2, use_container_width=True)

        s2 = comparison["team2"]["summary"]
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.metric("Tactical heart", s2["top_pagerank_player"])
        r2c2.metric("Key bridge", s2["top_betweenness_player"])
        r2c3.metric("Total passes", s2["total_passes"])

        st.dataframe(comparison["team2"]["metrics"].style.format({
            "in_degree": "{:.4f}", "out_degree": "{:.4f}",
            "total_degree": "{:.4f}", "betweenness": "{:.4f}",
            "pagerank": "{:.4f}",
        }), use_container_width=True)