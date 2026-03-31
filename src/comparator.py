import pandas as pd
import networkx as nx
from src.data_loader import get_team_passes_filtered
from src.network_builder import build_passing_network
from src.metrics import all_metrics


def compare_teams(
    match_id: int,
    team1: str,
    team2: str,
    period: int = None,
    starting_xi_only: bool = False
) -> dict:

    passes1 = get_team_passes_filtered(match_id, team1,
                                       period=period,
                                       starting_xi_only=starting_xi_only)
    passes2 = get_team_passes_filtered(match_id, team2,
                                       period=period,
                                       starting_xi_only=starting_xi_only)

    G1 = build_passing_network(passes1)
    G2 = build_passing_network(passes2)

    metrics1 = all_metrics(G1)
    metrics2 = all_metrics(G2)

    summary1 = _network_summary(G1, team1)
    summary2 = _network_summary(G2, team2)

    return {
        "team1": {
            "name": team1,
            "metrics": metrics1,
            "summary": summary1,
            "graph": G1,
            "passes": passes1
        },
        "team2": {
            "name": team2,
            "metrics": metrics2,
            "summary": summary2,
            "graph": G2,
            "passes": passes2
        },
    }


def _network_summary(G: nx.DiGraph, team: str) -> dict:
    if G.number_of_nodes() == 0:
        return {
            "team": team,
            "total_passes": 0,
            "density": 0,
            "top_pagerank_player": "N/A",
            "top_betweenness_player": "N/A",
            "avg_clustering": 0,
            "num_players": 0,
        }

    pagerank = nx.pagerank(G, weight="weight")
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    total_passes = sum(d["weight"] for _, _, d in G.edges(data=True))
    density = round(nx.density(G), 4)
    top_pagerank = max(pagerank, key=pagerank.get)
    top_betweenness = max(betweenness, key=betweenness.get)
    avg_clustering = round(nx.average_clustering(G.to_undirected()), 4)

    return {
        "team": team,
        "total_passes": total_passes,
        "density": density,
        "top_pagerank_player": top_pagerank,
        "top_betweenness_player": top_betweenness,
        "avg_clustering": avg_clustering,
        "num_players": G.number_of_nodes(),
    }


def compare_summary_df(comparison: dict) -> pd.DataFrame:
    s1 = comparison["team1"]["summary"]
    s2 = comparison["team2"]["summary"]

    df = pd.DataFrame({
        "metric": [
            "Total passes",
            "Network density",
            "Avg clustering",
            "Players used",
            "Top PageRank player",
            "Top betweenness player",
        ],
        s1["team"]: [
            s1["total_passes"],
            s1["density"],
            s1["avg_clustering"],
            s1["num_players"],
            s1["top_pagerank_player"],
            s1["top_betweenness_player"],
        ],
        s2["team"]: [
            s2["total_passes"],
            s2["density"],
            s2["avg_clustering"],
            s2["num_players"],
            s2["top_pagerank_player"],
            s2["top_betweenness_player"],
        ],
    })
    return df