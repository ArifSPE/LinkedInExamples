from __future__ import annotations

from html import escape
from typing import Iterable

from IPython.display import SVG, display


Node = tuple[str, str, int, int, str]
Edge = tuple[str, str]


def _arrow(x1: int, y1: int, x2: int, y2: int, color: str = "#475569") -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="2" marker-end="url(#arrowhead)" />'
    )


def render_svg_flow(
    title: str,
    nodes: Iterable[Node],
    edges: Iterable[Edge],
    width: int = 1200,
    height: int = 360,
    node_width: int = 190,
    node_height: int = 64,
) -> None:
    node_map = {name: (label, x, y, fill) for name, label, x, y, fill in nodes}

    edge_parts = []
    for src, dst in edges:
        _, x1, y1, _ = node_map[src]
        _, x2, y2, _ = node_map[dst]
        edge_parts.append(
            _arrow(
                x1 + node_width,
                y1 + node_height // 2,
                x2,
                y2 + node_height // 2,
            )
        )

    node_parts = []
    for _, label, x, y, fill in nodes:
        node_parts.append(
            (
                f'<rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" '
                f'rx="12" ry="12" fill="{fill}" stroke="#1f2937" stroke-width="1.5" />'
                f'<text x="{x + node_width // 2}" y="{y + node_height // 2 + 5}" '
                f'font-size="14" text-anchor="middle" fill="#0f172a" font-family="Arial, sans-serif">'
                f'{escape(label)}</text>'
            )
        )

    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#475569" />
        </marker>
      </defs>
      <rect x="0" y="0" width="{width}" height="{height}" fill="#f8fafc" rx="16" ry="16" />
      <text x="24" y="40" font-size="24" fill="#0f172a" font-family="Arial, sans-serif" font-weight="700">{escape(title)}</text>
      {''.join(edge_parts)}
      {''.join(node_parts)}
    </svg>
    """

    display(SVG(svg))
