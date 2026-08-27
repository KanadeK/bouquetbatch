from bouquetbatch.flow import MinCostFlow


def test_min_cost_flow_maximizes_flow_then_minimizes_cost() -> None:
    graph = MinCostFlow(4)
    graph.add_edge(0, 1, capacity=2, cost=0)
    graph.add_edge(0, 2, capacity=2, cost=0)
    graph.add_edge(1, 3, capacity=2, cost=5)
    graph.add_edge(2, 3, capacity=1, cost=1)

    flow, cost = graph.solve(0, 3)

    assert flow == 3
    assert cost == 11


def test_edge_exposes_resulting_flow() -> None:
    graph = MinCostFlow(2)
    edge = graph.add_edge(0, 1, capacity=7, cost=3)

    assert graph.solve(0, 1) == (7, 21)
    assert edge.flow == 7
