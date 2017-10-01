import collections


def calculate_postman_solution_stats(circuit, edge_weight_name='distance'):
    """
    Calculate summary stats on the route
    Args:
        circuit (list[tuple]): output from `cpp` or `rpp` solvers
        edge_weight_name (str): parameter name for edge attribute with distance/weight

    Returns:
        summary table (OrderedDict)
    """
    summary_stats = collections.OrderedDict()

    # Distance
    summary_stats['distance_walked'] = sum([e[3][edge_weight_name] for e in circuit])
    summary_stats['distance_doublebacked'] = sum([e[3][edge_weight_name] for e in circuit if 'augmented' in e[3]])
    summary_stats['distance_walked_once'] = summary_stats['distance_walked'] - summary_stats['distance_doublebacked']
    summary_stats['distance_walked_optional'] = sum([e[3]['distance'] for e in circuit if e[3].get('required') == 0])
    summary_stats['distance_walked_required'] = summary_stats['distance_walked'] - summary_stats['distance_walked_optional']

    # Number of edges
    summary_stats['edges_walked'] = len(circuit)
    summary_stats['edges_doublebacked'] = collections.Counter([e[3].get('augmented') for e in circuit])[True]
    summary_stats['edges_walked_once'] = summary_stats['edges_walked'] - summary_stats['edges_doublebacked']
    summary_stats['edges_walked_optional'] = collections.Counter([e[3].get('required') for e in circuit])[0]
    summary_stats['edges_walked_required'] = summary_stats['edges_walked'] - summary_stats['edges_walked_optional']

    return summary_stats
