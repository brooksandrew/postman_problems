#	File Created: 10/15/2020

"""
modified version of solver by brooksandrew
"""

import postman_problems.solver_lib as sl
from initialize_lib import turn_weight_function_distance, create_turn_weight_edge_attr
from postman_problems.graph import read_edgelist, create_networkx_graph_from_edgelist, create_required_graph, assert_graph_is_strongly_connected, create_eulerian_circuit

def rpp(edgelist_filename, complete_g, start_node=None, edge_weight='distance', turn_weight_coefficient=1):
    """
    Solving the RPP from beginning (load network data) to end (finding optimal route).  This optimization makes a
     relatively strong assumption: the starting graph must stay a connected graph when optional edges are removed.
    If this is not so, an assertion is raised.  This class of RPP generalizes to the CPP strategy.
    Args:
        edgelist_filename (str): filename of edgelist.  
        start_node (str): name of starting node.  
        edge_weight (str): name edge attribute that indicates distance to minimize in CPP
        turn_weight_coefficient (float): turn weight coefficient used to add turn_weight attributes to g_full
    Returns:
        list[tuple(str, str, dict)]:
        Each tuple is a direction (from one node to another) from the CPP solution route.
          The first element is the starting ("from") node.
          The second element is the end ("to") node.
          The third element is the dict of edge attributes for that edge.
    """

    el = read_edgelist(edgelist_filename)

    g_full = create_networkx_graph_from_edgelist(el)
    
    g_full, pos = sl.create_pos_and_add_to_graph(g_full, complete_g)
    
    g_full = create_turn_weight_edge_attr(g_full, length_weight='distance', normalization_coefficient=turn_weight_coefficient)

    g_req = create_required_graph(g_full)
    
    sl.visualize_g_req(g_req, pos)

    assert_graph_is_strongly_connected(g_req)

    g_aug = sl.make_graph_eulerian(g_req, g_full)

    sl.is_graph_eulerian(g_aug)

    circuit = list(create_eulerian_circuit(g_aug, g_full, str(start_node), edge_weight_name=turn_weight_function_distance))

    return circuit
