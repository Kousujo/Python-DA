"""Mạng lưới đồng tham gia sự kiện — cạnh giữa 2 thành viên = số sự
kiện họ cùng có mặt. Dùng networkx (thư viện mới, thêm vào requirements.txt).
"""

from __future__ import annotations

from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx

from src.models.club import Club


def build_coattendance_graph(club: Club) -> nx.Graph:
    """Dựng đồ thị: cạnh trọng số = số sự kiện 2 thành viên cùng có mặt."""
    df = club.to_dataframe()
    graph = nx.Graph()
    for member_id, member in club._members.items():
        graph.add_node(member_id, name=member.full_name, role=member.get_role_label())

    for _, group in df.groupby("event_id"):
        attendees = list(group["member_id"].unique())
        for m1, m2 in combinations(attendees, 2):
            if graph.has_edge(m1, m2):
                graph[m1][m2]["weight"] += 1
            else:
                graph.add_edge(m1, m2, weight=1)
    return graph


def plot_coattendance_network(graph: nx.Graph, save_path: str | None = None) -> plt.Figure:
    """Vẽ mạng lưới — node to = nhiều kết nối, màu cam = Ban chủ nhiệm."""
    fig, ax = plt.subplots(figsize=(9, 7))
    pos = nx.spring_layout(graph, seed=42, k=0.6)

    degrees = dict(graph.degree())
    node_sizes = [200 + degrees[n] * 40 for n in graph.nodes()]
    node_colors = [
        "#DD8452" if "Ban chủ nhiệm" in graph.nodes[n]["role"] else "#4C72B0"
        for n in graph.nodes()
    ]
    weights = [graph[u][v]["weight"] for u, v in graph.edges()]

    nx.draw_networkx_edges(graph, pos, width=[w * 0.6 for w in weights], edge_color="#B0B0B0", ax=ax)
    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, node_color=node_colors, ax=ax)
    labels = {n: graph.nodes[n]["name"].split()[-1] for n in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, ax=ax)

    ax.set_title("Mạng lưới đồng tham gia sự kiện")
    ax.axis("off")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig
