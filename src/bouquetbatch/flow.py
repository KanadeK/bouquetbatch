from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush


@dataclass(slots=True)
class Edge:
    to: int
    reverse: int
    capacity: int
    cost: int
    original_capacity: int

    @property
    def flow(self) -> int:
        return self.original_capacity - self.capacity


class MinCostFlow:
    def __init__(self, node_count: int) -> None:
        self.graph: list[list[Edge]] = [[] for _ in range(node_count)]

    def add_edge(self, source: int, target: int, capacity: int, cost: int) -> Edge:
        forward = Edge(
            to=target,
            reverse=len(self.graph[target]),
            capacity=capacity,
            cost=cost,
            original_capacity=capacity,
        )
        backward = Edge(
            to=source,
            reverse=len(self.graph[source]),
            capacity=0,
            cost=-cost,
            original_capacity=0,
        )
        self.graph[source].append(forward)
        self.graph[target].append(backward)
        return forward

    def solve(self, source: int, sink: int) -> tuple[int, int]:
        node_count = len(self.graph)
        potential = [0] * node_count
        total_flow = 0
        total_cost = 0
        infinity = 10**100

        while True:
            distance = [infinity] * node_count
            previous_node = [-1] * node_count
            previous_edge = [-1] * node_count
            distance[source] = 0
            queue: list[tuple[int, int]] = [(0, source)]

            while queue:
                current_distance, node = heappop(queue)
                if current_distance != distance[node]:
                    continue
                for edge_index, edge in enumerate(self.graph[node]):
                    if edge.capacity == 0:
                        continue
                    candidate = current_distance + edge.cost + potential[node] - potential[edge.to]
                    if candidate < distance[edge.to]:
                        distance[edge.to] = candidate
                        previous_node[edge.to] = node
                        previous_edge[edge.to] = edge_index
                        heappush(queue, (candidate, edge.to))

            if distance[sink] == infinity:
                break

            for node, node_distance in enumerate(distance):
                if node_distance != infinity:
                    potential[node] += node_distance

            added = infinity
            node = sink
            while node != source:
                parent = previous_node[node]
                edge = self.graph[parent][previous_edge[node]]
                added = min(added, edge.capacity)
                node = parent

            node = sink
            path_cost = 0
            while node != source:
                parent = previous_node[node]
                edge = self.graph[parent][previous_edge[node]]
                edge.capacity -= added
                self.graph[node][edge.reverse].capacity += added
                path_cost += edge.cost
                node = parent

            total_flow += added
            total_cost += added * path_cost

        return total_flow, total_cost
