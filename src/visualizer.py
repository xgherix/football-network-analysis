import networkx as nx
import pandas as pd
import plotly.graph_objects as go


def get_avg_positions(passes: pd.DataFrame) -> pd.DataFrame:
    records = []
    for player, group in passes.groupby("player"):
        xs, ys = [], []
        for loc in group["location"]:
            if isinstance(loc, list) and len(loc) == 2:
                xs.append(loc[0])
                ys.append(loc[1])
        if xs and ys:
            records.append({
                "player": player,
                "x": sum(xs) / len(xs),
                "y": sum(ys) / len(ys),
            })
    return pd.DataFrame(records).set_index("player")


def flip_coordinates(avg_positions: pd.DataFrame) -> pd.DataFrame:
    avg_positions = avg_positions.copy()
    avg_positions["x"] = 120 - avg_positions["x"]
    avg_positions["y"] = 80 - avg_positions["y"]
    return avg_positions


def draw_pitch_shapes():
    shapes = []
    shapes.append(dict(type="rect", x0=0, y0=0, x1=120, y1=80,
                       line=dict(color="white", width=2), fillcolor="#2d6a2d", layer="below"))
    shapes.append(dict(type="line", x0=60, y0=0, x1=60, y1=80,
                       line=dict(color="white", width=1.5), layer="below"))
    shapes.append(dict(type="circle", x0=51, y0=31, x1=69, y1=49,
                       line=dict(color="white", width=1.5), layer="below"))
    shapes.append(dict(type="circle", x0=59.5, y0=39.5, x1=60.5, y1=40.5,
                       line=dict(color="white", width=1), fillcolor="white", layer="below"))
    shapes.append(dict(type="rect", x0=0, y0=18, x1=18, y1=62,
                       line=dict(color="white", width=1.5), fillcolor="#2d6a2d", layer="below"))
    shapes.append(dict(type="rect", x0=0, y0=30, x1=6, y1=50,
                       line=dict(color="white", width=1.5), fillcolor="#2d6a2d", layer="below"))
    shapes.append(dict(type="rect", x0=102, y0=18, x1=120, y1=62,
                       line=dict(color="white", width=1.5), fillcolor="#2d6a2d", layer="below"))
    shapes.append(dict(type="rect", x0=114, y0=30, x1=120, y1=50,
                       line=dict(color="white", width=1.5), fillcolor="#2d6a2d", layer="below"))
    return shapes


def draw_passing_network(G: nx.DiGraph, passes: pd.DataFrame,
                         team_name: str = "Team", flip: bool = False,
                         color_metric: str = "pagerank"):

    avg_positions = get_avg_positions(passes)
    if flip:
        avg_positions = flip_coordinates(avg_positions)
    avg_positions = avg_positions[avg_positions.index.isin(G.nodes)]

    pagerank    = nx.pagerank(G, weight="weight")
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)
    in_degree   = nx.in_degree_centrality(G)
    out_degree  = nx.out_degree_centrality(G)

    metric_map = {
        "pagerank":    (pagerank,    "PageRank",    "Oranges"),
        "betweenness": (betweenness, "Betweenness", "Blues"),
        "in_degree":   (in_degree,   "In-degree",   "Greens"),
        "out_degree":  (out_degree,  "Out-degree",  "Purples"),
    }

    metric_values, metric_label, colorscale = metric_map[color_metric]
    max_pr         = max(pagerank.values())      if pagerank      else 1
    max_metric_val = max(metric_values.values()) if metric_values else 1

    pass_counts = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    max_weight  = max(pass_counts.values()) if pass_counts else 1

    edge_traces = []
    for (u, v), weight in pass_counts.items():
        if u in avg_positions.index and v in avg_positions.index:
            x0, y0 = avg_positions.loc[u, "x"], avg_positions.loc[u, "y"]
            x1, y1 = avg_positions.loc[v, "x"], avg_positions.loc[v, "y"]
            alpha = round(0.15 + 0.6 * (weight / max_weight), 2)
            width = 0.5 + 4 * (weight / max_weight)
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(width=width, color=f"rgba(255,255,255,{alpha})"),
                hoverinfo="none",
                showlegend=False
            ))

    node_x     = []
    node_y     = []
    node_size  = []
    node_color = []
    node_hover = []

    for player, row in avg_positions.iterrows():
        pr           = pagerank.get(player, 0)
        bw           = betweenness.get(player, 0)
        ind          = in_degree.get(player, 0)
        oud          = out_degree.get(player, 0)
        total_passes = sum(G[player][v]["weight"] for v in G.successors(player))
        received     = sum(G[u][player]["weight"] for u in G.predecessors(player))
        metric_val   = metric_values.get(player, 0)

        node_x.append(float(row["x"]))
        node_y.append(float(row["y"]))
        node_size.append(30 + 50 * (pr / max_pr))
        node_color.append(float(metric_val))
        node_hover.append(
            f"<b>{player}</b><br>"
            f"{metric_label}: {metric_val:.4f}<br>"
            f"PageRank: {pr:.4f}<br>"
            f"Betweenness: {bw:.4f}<br>"
            f"In-degree: {ind:.4f}<br>"
            f"Out-degree: {oud:.4f}<br>"
            f"Passes made: {total_passes}<br>"
            f"Passes received: {received}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_hover,
        hoverlabel=dict(
            bgcolor="black",
            bordercolor="white",
            font=dict(color="white", size=13)
        ),
        marker=dict(
            symbol="circle",
            size=node_size,
            color=node_color,
            colorscale=colorscale,
            cmin=0,
            cmax=max_metric_val,
            showscale=True,
            colorbar=dict(
                title=dict(text=metric_label, font=dict(color="white")),
                tickfont=dict(color="white"),
            ),
            line=dict(color="white", width=2),
        ),
        showlegend=False
    )

    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            title=dict(
                text=f"{team_name} — passing network — colored by {metric_label}",
                font=dict(color="white", size=18),
                x=0.5
            ),
            plot_bgcolor="#2d6a2d",
            paper_bgcolor="#1a1a2e",
            shapes=draw_pitch_shapes(),
            xaxis=dict(
                range=[0, 120],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True,
            ),
            yaxis=dict(
                range=[0, 80],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True,
            ),
            margin=dict(l=20, r=100, t=60, b=20),
            height=720,
            width=1200,
            hovermode="closest"
        )
    )
    return fig


def save_figure(fig, path: str):
    fig.write_html(path)
    print(f"saved to {path}")