import itertools
import warnings
import pandas as pd
import networkx as nx


def read_edgelist(edgelist_filename):
    """
    Read an edgelist table into a pandas dataframe
    Args:
        edgelist_filename (str): filename of edgelist.  See cpp.py for more details.
    Returns:
        pandas dataframe of edgelist
    """
    el = pd.read_csv(edgelist_filename)
    el = el.dropna()  # drop rows with all NAs... as I find CSVs created w Numbers annoyingly do.

    assert 'augmented' not in el.columns, \
        'Edgelist cannot contain a column named "augmented", sorry. This will cause computation problems'

    if 'id' in el.columns:
        warnings.warn("Edgelist contains field named 'id'.  This is a field that will be assigned to edge attributes"
                      "with the `create_networkx_graph_from_edgelist function.  That is OK though.  We'll use your 'id'"
                      "field if it is unique.")
        assert el['id'].nunique() == len(el), 'Provided edge "id" field is not unique.  Please drop "id" or try again.'
    return el


def create_networkx_graph_from_edgelist(edgelist, edge_id='id'):
    """
    Create a networkx MultiGraph object from an edgelist (pandas dataframe).
    Used to create the user's starting graph for which a CPP solution is desired.

    Args:
        edgelist (pandas dataframe): output of `read_edgelist` function.
            The first two columns are treated as source and target node names.
            The following columns are treated as edge attributes.
        edge_id (str): name of edge attribute which will be used in `create_eulerian_circuit`.

    Returns:
        networkx.MultiGraph:
            Returning a MultiGraph rather than Graph to support parallel edges
    """
    g = nx.MultiGraph()
    if edge_id in edgelist.columns:
        warnings.warn('{} is already an edge attribute in `edgelist`.  We will try to use it, but recommend '
                      'renaming this column in your edgelist to allow this function to create it in a standardized way'
                      'where it is guaranteed to be unique'.format(edge_id))

    for i, row in enumerate(edgelist.iterrows()):
        edge_attr_dict = row[1][2:].to_dict()
        if edge_id not in edge_attr_dict:
            edge_attr_dict[edge_id] = i
        g.add_edge(row[1][0], row[1][1], attr_dict=edge_attr_dict)
    return g


def _get_even_or_odd_nodes(graph, mod):
    """
    Helper function for get_even_nodes.  Given a networkx object, return names of the odd or even nodes
    Args:
        graph (networkx graph): determine the degree of nodes in this graph
        mod (int): 0 for even, 1 for odd

    Returns:
        list[str]: list of node names of odd or even degree
    """
    degree_nodes = []
    for v, d in graph.degree_iter():
        if d % 2 == mod:
            degree_nodes.append(v)
    return degree_nodes


def get_odd_nodes(graph):
    """
    Given a networkx object, return names of the odd degree nodes

    Args:
        graph (networkx graph): graph used to list odd degree nodes for

    Returns:
        list[str]: names of nodes with odd degree
    """
    return _get_even_or_odd_nodes(graph, 1)


def get_even_nodes(graph):
    """
    Given a networkx object, return names of the even degree nodes

    Args:
        graph (networkx graph): graph used to list even degree nodes for

    Returns:
        list[str]: names of nodes with even degree

    """
    return _get_even_or_odd_nodes(graph, 0)


def get_shortest_paths_distances(graph, pairs, edge_weight_name='distance'):
    """
    Calculate shortest distance between each pair of nodes in a graph

    Args:
        graph (networkx graph)
        pairs (list[2tuple]): List of length 2 tuples containing node pairs to calculate shortest path between
        edge_weight_name (str): edge attribute used for distance calculation

    Returns:
        dict: mapping each pair in `pairs` to the shortest path using `edge_weight_name` between them.
    """
    distances = {}
    for pair in pairs:
        distances[pair] = nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name)
    return distances


def create_complete_graph(pair_weights, flip_weights=True):
    """
    Create a perfectly connected graph from a list of node pairs and the distances between them.

    Args:
        pair_weights (dict): mapping between node pairs and distance calculated in `get_shortest_paths_distances`.
        flip_weights (Boolean): True negates the distance in `pair_weights`.  We negate whenever we want to find the
         minimum weight matching on a graph because networkx has only `max_weight_matching`, no `min_weight_matching`.

    Returns:
        complete (fully connected graph) networkx graph using the node pairs and distances provided in `pair_weights`
    """
    g = nx.Graph()
    for k, v in pair_weights.items():
        wt_i = -v if flip_weights else v
        g.add_edge(k[0], k[1], attr_dict={'distance': v, 'weight': wt_i})
    return g


def dedupe_matching(matching):
    """
    Remove duplicates node pairs from the output of networkx.algorithms.max_weight_matching since we don't care about order.

    Args:
        matching (dict): output from networkx.algorithms.max_weight_matching.  key is "from" node, value is "to" node.

    Returns:
        list[2tuples]: list of node pairs from `matching` deduped (ignoring order).
    """
    matched_pairs_w_dupes = [tuple(sorted([k, v])) for k, v in matching.items()]
    return list(pd.unique(matched_pairs_w_dupes))


def add_augmenting_path_to_graph(graph, min_weight_pairs, edge_weight_name='weight'):
    """
    Add the min weight matching edges to the original graph
    Note the resulting graph could (and likely will) have edges that didn't exist on the original graph.  To get the
    true circuit, we must breakdown these augmented edges into the shortest path through the edges that do exist.  This
    is done with `create_eulerian_circuit`.

    Args:
        graph (networkx graph):
        min_weight_pairs (list[2tuples): output of `dedupe_matching` specifying the odd degree nodes to link together
        edge_weight_name (str): edge attribute used for distance calculation

    Returns:
        networkx graph: `graph` augmented with edges between the odd nodes specified in `min_weight_pairs`
    """
    graph_aug = graph.copy()  # so we don't mess with the original graph
    for pair in min_weight_pairs:
        graph_aug.add_edge(pair[0],
                           pair[1],
                           attr_dict={'distance': nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name),
                                      'augmented': True}
                           )
    return graph_aug


def create_eulerian_circuit(graph_augmented, graph_original, start_node=None):
    """
    networkx.eulerian_circuit only returns the order in which we hit each node.  It does not return the attributes of the
    edges needed to complete the circuit.  This is necessary for the postman problem where we need to keep track of which
    edges have been covered already when multiple edges exist between two nodes.
    We also need to annotate the edges added to make the eulerian to follow the actual shortest path trails (not
    the direct shortest path pairings between the odd nodes for which there might not be a direct trail)

    Args:
        graph_augmented (networkx graph): graph w links between odd degree nodes created from `add_augmenting_path_to_graph`.
        graph_original (networkx graph): orginal graph created from `create_networkx_graph_from_edgelist`
        start_node (str): name of starting (and ending) node for CPP solution.

    Returns:
        networkx graph (`graph_original`) augmented with edges directly between the odd nodes
    """

    euler_circuit = list(nx.eulerian_circuit(graph_augmented, source=start_node))
    assert len(graph_augmented.edges()) == len(euler_circuit), 'graph and euler_circuit do not have equal number of edges.'
    edge_data = graph_augmented.edges(data=True)

    for edge in euler_circuit:
        possible_edges = [e for e in edge_data if set([e[0], e[1]]) == set([edge[0], edge[1]])]

        edge_key = 0  # initialize w 0.  Could change w parallel edges.
        if possible_edges[edge_key][2].get('augmented'):
            # find shortest path from odd node to odd node in original graph (could be nonadjacent)
            aug_path = nx.shortest_path(graph_original, edge[0], edge[1], weight='distance')

            # for each shortest path between odd nodes, add shortest path through edges that actually exist to circuit
            for edge_aug in list(zip(aug_path[:-1], aug_path[1:])):
                # find edge with shortest distance (if there are two parallel edges between the same nodes)
                edge_aug_dict = graph_original[edge_aug[0]][edge_aug[1]]
                edge_key = min(edge_aug_dict.keys(), key=(lambda k: edge_aug_dict[k]['distance']))  # index with min distance
                edge_aug_shortest = edge_aug_dict[edge_key]
                edge_aug_shortest['augmented'] = True
                edge_aug_shortest['id'] = edge_aug_dict[edge_key]['id']
                yield(edge_aug + (edge_aug_shortest,))
        else:
            yield(edge + (possible_edges[edge_key][2],))
        edge_data.remove(possible_edges[edge_key])


def cpp(edgelist_filename, start_node=None, edge_weight='distance'):
    """
    Solving the CPP from beginning (load network data) to end (finding optimal route).
    Can be run from command line with arguments from cpp.py, or from an interactive Python session (ex jupyter notebook)

    Args:
        edgelist_filename (str): filename of edgelist.  See cpp.py for more details
        start_node (str): name of starting node.  See cpp.py for more details
        edge_weight (str): name edge attribute that indicates distance to minimize in CPP

    Returns:
        tuple(list[tuple(str, str, dict)], networkx.MultiGraph]:
        Each tuple is a direction (from one node to another) from the CPP solution route.
          The first element is the starting ("from") node.
          The second element is the end ("to") node.
          The third element is the dict of edge attributes for that edge.
        The original graph is returned as well.  This is needed for visualization
    """
    el = read_edgelist(edgelist_filename)
    g = create_networkx_graph_from_edgelist(el)

    # get augmenting path for odd nodes
    odd_nodes = get_odd_nodes(g)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(g, odd_node_pairs, edge_weight)
    g_odd_complete = create_complete_graph(odd_node_pairs_shortest_paths, flip_weights=True)

    # best solution using blossom algorithm
    odd_matching = dedupe_matching(nx.algorithms.max_weight_matching(g_odd_complete, True))

    # add the min weight matching edges to g
    g_aug = add_augmenting_path_to_graph(g, odd_matching)

    # get eulerian circuit route.
    circuit = list(create_eulerian_circuit(g_aug, g, start_node))

    return circuit, g


