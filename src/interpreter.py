import networkx as nx
import pandas as pd
from src.metrics import all_metrics


def interpret_player_roles(G: nx.DiGraph, metrics_df: pd.DataFrame) -> dict:
    if metrics_df.empty:
        return {}

    playmaker = metrics_df.loc[metrics_df["pagerank"].idxmax(), "player"]
    bridge = metrics_df.loc[metrics_df["betweenness"].idxmax(), "player"]
    ball_carrier = metrics_df.loc[metrics_df["out_degree"].idxmax(), "player"]
    target = metrics_df.loc[metrics_df["in_degree"].idxmax(), "player"]

    isolated = metrics_df[metrics_df["total_degree"] < metrics_df["total_degree"].quantile(0.25)]["player"].tolist()

    return {
        "playmaker": playmaker,
        "bridge": bridge,
        "ball_carrier": ball_carrier,
        "target": target,
        "isolated": isolated,
    }


def interpret_network_style(density: float, clustering: float) -> str:
    if density >= 0.5 and clustering >= 0.75:
        return "High-possession, combination-based play — short passes, triangles, high player involvement."
    elif density >= 0.5 and clustering < 0.75:
        return "High possession but more direct — many players involved but fewer combination triangles."
    elif density < 0.5 and clustering >= 0.75:
        return "Compact and structured — fewer passing options but strong local combinations."
    else:
        return "Direct and vertical play — low possession, few passing combinations, fast transitions."


def interpret_match(
    team: str,
    G: nx.DiGraph,
    passes: pd.DataFrame,
    total_passes: int,
    density: float,
    clustering: float,
    opponent: str = None,
    opponent_passes: int = None,
) -> str:

    metrics_df = all_metrics(G)
    roles = interpret_player_roles(G, metrics_df)
    style = interpret_network_style(density, clustering)

    pagerank_val = metrics_df.loc[metrics_df["pagerank"].idxmax(), "pagerank"]
    betweenness_val = metrics_df.loc[metrics_df["betweenness"].idxmax(), "betweenness"]
    out_degree_val = metrics_df.loc[metrics_df["out_degree"].idxmax(), "out_degree"]
    in_degree_val = metrics_df.loc[metrics_df["in_degree"].idxmax(), "in_degree"]

    lines = []

    if opponent and opponent_passes:
        diff = total_passes - opponent_passes
        pct = round(abs(diff) / opponent_passes * 100)
        if diff > 0:
            lines.append(
                f"**{team}** dominated possession with **{total_passes} passes** — "
                f"**{pct}% more** than {opponent} ({opponent_passes} passes)."
            )
        else:
            lines.append(
                f"**{team}** had less possession with **{total_passes} passes** — "
                f"**{pct}% fewer** than {opponent} ({opponent_passes} passes)."
            )
    else:
        lines.append(f"**{team}** completed **{total_passes} successful passes** during this match.")

    lines.append(
        f"**Tactical style:** {style}"
    )

    lines.append(
        f"**Tactical heart — {roles['playmaker']}** (PageRank: {pagerank_val:.4f}): "
        f"The most influential player in the passing network. Receives passes from key teammates "
        f"and redistributes across all areas of the pitch."
    )

    lines.append(
        f"**Key bridge — {roles['bridge']}** (Betweenness: {betweenness_val:.4f}): "
        f"The most critical connector in the team. Removing this player would fragment "
        f"the passing structure the most."
    )

    lines.append(
        f"**Main distributor — {roles['ball_carrier']}** (Out-degree: {out_degree_val:.4f}): "
        f"Passes to the highest number of different teammates — the primary ball distributor."
    )

    lines.append(
        f"**Most sought player — {roles['target']}** (In-degree: {in_degree_val:.4f}): "
        f"Receives passes from the highest number of different teammates — "
        f"the primary target in build-up play."
    )

    if roles["isolated"]:
        names = ", ".join(roles["isolated"])
        lines.append(
            f"**Low involvement players — {names}**: "
            f"These players had fewer passing connections than 75% of their teammates, "
            f"suggesting limited integration in the passing network."
        )

    return "\n\n".join(lines)


def compare_interpretation(comparison: dict) -> str:
    t1 = comparison["team1"]
    t2 = comparison["team2"]

    s1 = t1["summary"]
    s2 = t2["summary"]

    lines = []

    pass_diff = abs(s1["total_passes"] - s2["total_passes"])
    dominant = s1["team"] if s1["total_passes"] > s2["total_passes"] else s2["team"]
    other = s2["team"] if dominant == s1["team"] else s1["team"]
    lines.append(
        f"**{dominant}** controlled the match with significantly more passes "
        f"(**{pass_diff} more** than {other})."
    )

    if s1["density"] > s2["density"]:
        lines.append(
            f"**{s1['team']}** had a denser passing network ({s1['density']} vs {s2['density']}), "
            f"indicating more players were involved in build-up play."
        )
    else:
        lines.append(
            f"**{s2['team']}** had a denser passing network ({s2['density']} vs {s1['density']}), "
            f"indicating more players were involved in build-up play despite fewer passes."
        )

    if s1["avg_clustering"] > s2["avg_clustering"]:
        lines.append(
            f"**{s1['team']}** showed stronger combination play (clustering: {s1['avg_clustering']} "
            f"vs {s2['avg_clustering']}), forming more passing triangles between players."
        )
    else:
        lines.append(
            f"**{s2['team']}** showed stronger combination play (clustering: {s2['avg_clustering']} "
            f"vs {s1['avg_clustering']}), forming more passing triangles between players."
        )

    lines.append(
        f"**{s1['team']}'s tactical heart:** {s1['top_pagerank_player']} — "
        f"**{s2['team']}'s tactical heart:** {s2['top_pagerank_player']}."
    )

    lines.append(
        f"**{s1['team']}'s key bridge:** {s1['top_betweenness_player']} — "
        f"**{s2['team']}'s key bridge:** {s2['top_betweenness_player']}."
    )

    return "\n\n".join(lines)