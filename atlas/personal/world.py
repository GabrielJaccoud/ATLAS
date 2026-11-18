from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldNode:
    node_id: str
    kind: str
    name: str
    attributes: dict[str, object]


@dataclass(frozen=True)
class WorldEdge:
    source: str
    relation: str
    target: str
    weight: float = 1.0


class MyWorldGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, WorldNode] = {}
        self.edges: list[WorldEdge] = []

    def add_node(self, node: WorldNode) -> None:
        self.nodes[node.node_id] = node

    def connect(self, edge: WorldEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Both nodes must exist.")
        self.edges.append(edge)

    def neighbors(self, node_id: str) -> tuple[WorldNode, ...]:
        ids = {
            e.target for e in self.edges if e.source == node_id
        } | {
            e.source for e in self.edges if e.target == node_id
        }
        return tuple(self.nodes[i] for i in sorted(ids))
