# modified version of function by brooksandrew

import collections

def calculate_postman_solution_stats(circuit, edge_weight_name='distance'):
    #JC modified for directed graphs
    """
    Calculate summary stats on the route
    Args:
        circuit (list[tuple]): output from `cpp` or `rpp` solvers
        edge_weight_name (str): parameter name for edge attribute with distance/weight
    Returns:
        print statements with relevant data
        summary table (OrderedDict)
    """
    summary_stats = collections.OrderedDict()

    undirected_edge_passes = {}
    for e in circuit:
        edge = frozenset([e[0], e[1]])
        if edge not in undirected_edge_passes:
            undirected_edge_passes[edge] = {'edge_distance' : e[3][edge_weight_name], 'number_of_passes' : 1}
        else:
            undirected_edge_passes[edge]['number_of_passes'] += 1

    directed_edges = []
    for e in circuit:
        edge = (e[0], e[1])
        if edge not in directed_edges:
            directed_edges += [edge]
            
    summary_stats['distance_traveled'] = sum([e[3][edge_weight_name] for e in circuit])
    summary_stats['distance_in_circuit'] = sum([undirected_edge_passes[edge]['edge_distance'] for edge in undirected_edge_passes])
    summary_stats['distance_traveled_once'] = sum([undirected_edge_passes[edge]['edge_distance'] for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 1])
    summary_stats['distance_traveled_twice'] = sum([undirected_edge_passes[edge]['edge_distance']*2 for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 2])
    summary_stats['distance_traveled_thrice'] = sum([undirected_edge_passes[edge]['edge_distance']*3 for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 3])
    summary_stats['distance_traveled_more_than_thrice'] = sum([undirected_edge_passes[edge]['edge_distance']*undirected_edge_passes[edge]['number_of_passes'] for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] > 3])
    summary_stats['road_length_traveled_more_than_thrice'] = sum([undirected_edge_passes[edge]['edge_distance'] for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] > 3])
    summary_stats['distance_traveled_optional'] = sum([e[3]['distance'] for e in circuit if e[3].get('required') == 0])
    summary_stats['distance_traveled_required'] = summary_stats['distance_traveled'] - summary_stats['distance_traveled_optional']

    summary_stats['edges_traveled'] = len(circuit)
    summary_stats['edges_in_circuit'] = len(undirected_edge_passes)
    summary_stats['directed_edges'] = len(directed_edges)
    summary_stats['edges_traveled_once'] = len([edge for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 1])
    summary_stats['edges_traveled_twice'] = len([edge for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 2])
    summary_stats['edges_traveled_thrice'] = len([edge for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] == 3])
    summary_stats['edges_traveled_more_than_thrice'] = len([edge for edge in undirected_edge_passes if undirected_edge_passes[edge]['number_of_passes'] > 3])
    summary_stats['edges_traveled_optional'] = collections.Counter([e[3].get('required') for e in circuit])[0]
    summary_stats['edges_traveled_required'] = summary_stats['edges_traveled'] - summary_stats['edges_traveled_optional']

    print('\nRoute Statistics\n')

    print('\tTotal Distance Traveled: {} miles'.format(round(summary_stats['distance_traveled']*0.000621371, 2)))
    print('\t\tRoad Length Covered by Circuit: {} miles'.format(round(summary_stats['distance_in_circuit']*0.000621371, 2)))
    print('\tDistance Traveled Once: {} miles'.format(round(summary_stats['distance_traveled_once']*0.000621371, 2)))
    print('\tDistance Traveled Twice: {} miles'.format(round(summary_stats['distance_traveled_twice']*0.000621371, 2)))
    print('\t\tRoad Length Traveled Twice: {} miles'.format(round(summary_stats['distance_traveled_twice']*0.000621371/2, 2)))
    print('\tDistance Traveled Thrice: {} miles'.format(round(summary_stats['distance_traveled_thrice']*0.000621371, 2)))
    print('\t\tRoad Length Traveled Thrice: {} miles'.format(round(summary_stats['distance_traveled_thrice']*0.000621371/3, 2)))
    print('\tDistance Traveled more than Thrice: {} miles'.format(round(summary_stats['distance_traveled_more_than_thrice']*0.000621371, 2)))
    print('\t\tRoad Length Traveled more than Thrice: {} miles'.format(round(summary_stats['road_length_traveled_more_than_thrice']*0.000621371, 2)))
    print('\tDistance of Passes over Required Edges: {} miles'.format(round(summary_stats['distance_traveled_required']*0.000621371, 2)))
    print('\tDistance of Passes over Optional Edges: {} miles\n'.format(round(summary_stats['distance_traveled_optional']*0.000621371, 2)))

    print('\tNumber of Edge Passes: {}'.format(summary_stats['edges_traveled']))
    print('\tNumber of Directed Edges in Circuit: {}'.format(summary_stats['directed_edges']))
    print('\tNumber of Undirected Edges in Circuit: {}'.format(summary_stats['edges_in_circuit']))
    print('\t\tNumber Traveled Once: {}'.format(summary_stats['edges_traveled_once']))
    print('\t\tNumber Traveled Twice: {}'.format(summary_stats['edges_traveled_twice']))
    print('\t\tNumber Traveled Thrice: {}'.format(summary_stats['edges_traveled_thrice']))
    print('\t\tNumber Traveled More than Thrice: {}'.format(summary_stats['edges_traveled_more_than_thrice']))
    print('\tNumber of Passes over Required Edges: {}'.format(summary_stats['edges_traveled_required']))
    print('\tNumber of Passes over Optional Edges: {}'.format(summary_stats['edges_traveled_optional']))

    return summary_stats
