import networkx as nx
import pandas as pd

def degree_centrality(G: nx.DiGraph) -> pd.DataFrame:
    in_degree = nx.in_degree_centrality(G)
    out_degree = nx.out_degree_centrality(G)

    df = pd.DataFrame({
        "player": list(in_degree.keys()),
        "in_degree": list(in_degree.values()),
        "out_degree": list(out_degree.values()),
    })

    df["total_degree"] = df["in_degree"] + df["out_degree"]
    df = df.sort_values("total_degree", ascending=False).reset_index(drop=True)
    return df

def betweenness_centrality(G: nx.DiGraph) -> pd.DataFrame:
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    df = pd.DataFrame({
        "player": list(betweenness.keys()),
        "betweenness": list(betweenness.values()),
    })

    df = df.sort_values("betweenness", ascending=False).reset_index(drop=True)
    return df

def pagerank(G: nx.DiGraph) -> pd.DataFrame:
    pr = nx.pagerank(G, weight="weight")

    df = pd.DataFrame({
    "player": list(pr.keys()),
    "pagerank": list(pr.values()),
    })

    df = df.sort_values("pagerank", ascending=False).reset_index(drop=True)
    return df

def all_metrics(G: nx.DiGraph) -> pd.DataFrame:
    deg = degree_centrality(G).set_index("player")
    bet = betweenness_centrality(G).set_index("player")
    pr = pagerank(G).set_index("player")

    combined = deg.join(bet).join(pr)
    combined = combined.sort_values("pagerank", ascending=False).reset_index()
    return combined