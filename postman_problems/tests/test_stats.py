from postman_problems.stats import calculate_postman_solution_stats


def test_stats_on_simple_graph_required_edges_only(GRAPH_1_CIRCUIT_CPP):
    stats = calculate_postman_solution_stats(GRAPH_1_CIRCUIT_CPP)
    assert isinstance(stats, dict)

    assert stats['distance_walked'] == 45
    assert stats['distance_doublebacked'] == 5
    assert stats['distance_walked_once'] == 40
    assert stats['distance_walked_required'] == 45
    assert stats['distance_walked_optional'] == 0

    assert stats['edges_walked'] == 7
    assert stats['edges_doublebacked'] == 2
    assert stats['edges_walked_once'] == 5
    assert stats['edges_walked_required'] == 7
    assert stats['edges_walked_optional'] == 0


def test_stats_on_star_graph_with_optional_edges(GRAPH_2_CIRCUIT_RPP):
    stats = calculate_postman_solution_stats(GRAPH_2_CIRCUIT_RPP)
    assert isinstance(stats, dict)

    assert stats['distance_walked'] == 116
    assert stats['distance_doublebacked'] == 6
    assert stats['distance_walked_once'] == 110
    assert stats['distance_walked_required'] == 110
    assert stats['distance_walked_optional'] == 6

    assert stats['edges_walked'] == 6
    assert stats['edges_doublebacked'] == 2
    assert stats['edges_walked_once'] == 4
    assert stats['edges_walked_required'] == 4
    assert stats['edges_walked_optional'] == 2

