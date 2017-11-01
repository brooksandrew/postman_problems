import itertools
import logging
import networkx as nx

from postman_problems.graph import read_edgelist, create_networkx_graph_from_edgelist, create_required_graph, \
    assert_graph_is_connected, get_odd_nodes, get_shortest_paths_distances, create_complete_graph, dedupe_matching, \
    add_augmenting_path_to_graph, create_eulerian_circuit


logger_rpp = logging.getLogger('{0}.{1}'.format(__name__, 'rpp'))
logger_cpp = logging.getLogger('{0}.{1}'.format(__name__, 'cpp'))


def rpp(edgelist_filename, start_node=None, edge_weight='distance', verbose=False):
    """
    Solving the RPP from beginning (load network data) to end (finding optimal route).  This optimization makes a
     relatively strong assumption: the starting graph must stay a connected graph when optional edges are removed.
    If this is not so, an assertion is raised.  This class of RPP generalizes to the CPP strategy.

    Args:
        edgelist_filename (str): filename of edgelist.  See cpp.py for more details
        start_node (str): name of starting node.  See cpp.py for more details
        edge_weight (str): name edge attribute that indicates distance to minimize in CPP
        verbose (boolean): log info messages?

    Returns:
        tuple(list[tuple(str, str, dict)], networkx.MultiGraph]:
        Each tuple is a direction (from one node to another) from the CPP solution route.
          The first element is the starting ("from") node.
          The second element is the end ("to") node.
          The third element is the dict of edge attributes for that edge.
        The original graph is returned as well.  This is needed for visualization
    """

    logger_rpp.disabled = not verbose

    logger_rpp.info('read edgelist')
    el = read_edgelist(edgelist_filename, keep_optional=True)

    logger_rpp.info('create full and required graph')
    g_full = create_networkx_graph_from_edgelist(el)
    g_req = create_required_graph(g_full)
    assert_graph_is_connected(g_req)

    logger_rpp.info('getting odd node pairs')
    odd_nodes = get_odd_nodes(g_req)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))

    logger_rpp.info('get shortest paths between odd nodes')
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(g_full, odd_node_pairs, edge_weight)

    logger_rpp.info('Find min weight matching using blossom algorithm')
    g_odd_complete = create_complete_graph(odd_node_pairs_shortest_paths, flip_weights=True)
    odd_matching = dedupe_matching(nx.algorithms.max_weight_matching(g_odd_complete, True))

    logger_rpp.info('add the min weight matching edges to g')
    g_aug = add_augmenting_path_to_graph(g_req, odd_matching)

    logger_rpp.info('get eulerian circuit route')
    circuit = list(create_eulerian_circuit(g_aug, g_full, start_node))

    return circuit, g_full


def cpp(edgelist_filename, start_node=None, edge_weight='distance', verbose=False):
    """
    Solving the CPP from beginning (load network data) to end (finding optimal route).
    Can be run from command line with arguments from cpp.py, or from an interactive Python session (ex jupyter notebook)

    Args:
        edgelist_filename (str): filename of edgelist.  See cpp.py for more details
        start_node (str): name of starting node.  See cpp.py for more details
        edge_weight (str): name edge attribute that indicates distance to minimize in CPP
        verbose (boolean): log info messages?

    Returns:
        tuple(list[tuple(str, str, dict)], networkx.MultiGraph]:
        Each tuple is a direction (from one node to another) from the CPP solution route.
          The first element is the starting ("from") node.
          The second element is the end ("to") node.
          The third element is the dict of edge attributes for that edge.
        The original graph is returned as well.  This is needed for visualization
    """
    logger_cpp.disabled = not verbose

    logger_cpp.info('read edgelist and create base graph')
    el = read_edgelist(edgelist_filename, keep_optional=False)
    g = create_networkx_graph_from_edgelist(el)

    logger_cpp.info('get augmenting path for odd nodes')
    odd_nodes = get_odd_nodes(g)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(g, odd_node_pairs, edge_weight)
    g_odd_complete = create_complete_graph(odd_node_pairs_shortest_paths, flip_weights=True)

    logger_cpp.info('Find min weight matching using blossom algorithm')
    odd_matching = dedupe_matching(nx.algorithms.max_weight_matching(g_odd_complete, True))

    logger_cpp.info('add the min weight matching edges to g')
    g_aug = add_augmenting_path_to_graph(g, odd_matching)

    logger_cpp.info('get eulerian circuit route')
    circuit = list(create_eulerian_circuit(g_aug, g, start_node))

    return circuit, g
