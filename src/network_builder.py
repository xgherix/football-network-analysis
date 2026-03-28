import networkx as nx
import pandas as pd

def build_passing_network(passes: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()

    for _, row in passes.iterrows():
        passer = row["player"]
        recipient = row["pass_recipient"]

        if pd.isna(recipient):
            continue

        if G.has_edge(passer, recipient):
            G[passer][recipient]["weight"] +=1
        else:
            G.add_edge(passer, recipient, weight=1)

    return G

def add_player_positions(G: nx.DiGraph, passes: pd.DataFrame) -> nx.DiGraph:
    positions = passes.groupby("player")[["location"]].first()

    for player, row in positions.iterrows():
        if player in G.nodes:
            loc = row["location"]
            if isinstance(loc, list) and len(loc) == 2:
                G.nodes[player]["x"] = loc[0]
                G.nodes[player]["y"] = loc[1]
    return G

def get_network_summary(G: nx.DiGraph) -> dict:
    return {
        "players": G.number_of_nodes(),
        "passing_combinations": G.number_of_edges(),
        "total_passes": sum(d["weight"] for _, _, d in G.edges(data=True)),
        "density": round(nx.density(G), 4),
    }