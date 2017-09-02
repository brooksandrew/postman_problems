import itertools
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
    return el


def create_networkx_graph_from_edgelist(edgelist):
    """
    Create a networkx object from an edgelist (pandas dataframe)

    Args:
        edgelist (pandas dataframe): output of read_edgelist function.
            The first two columns are treated as source and target vertex names.
            The following columns are treated as edge attributes.

    Returns:
        networkx.MultiGraph:
            Returning a MultiGraph rather than Graph to support parallel edges
    """
    g = nx.MultiGraph()
    for row in edgelist.iterrows():
        edge_attr_dict = row[1][2:].to_dict()
        g.add_edge(row[1][0], row[1][1], attr_dict=edge_attr_dict)
    return g


def add_node_attributes(graph, nodelist):
    """
    Adds node attributes to graph.  Only used for visualization.

    Args:
        graph (networkx graph): graph you want to add node attributes to
        nodelist (pandas dataframe): containing node attributes.
            Expects a column named 'id' specifying the node names from `graph`.
            Other columns should specify desired node attributes.
            First row should include attribute names.

    Returns:
        networkx graph: original `graph` augmented w node attributes
    """
    for i, row in nodelist.iterrows():
        graph.node[row['id']] = row.to_dict()
    return graph


def _get_even_or_odd_vertices(graph, mod):
    """Helper function: given a networkx object, return names of the odd (mod=1) or even (mod=0) vertices"""
    degree_vertices = []
    for v, d in graph.degree_iter():
        if d % 2 == mod:
            degree_vertices.append(v)
    return degree_vertices


def get_odd_vertices(graph):
    """Given a networkx object, return names of the odd vertices"""
    return _get_even_or_odd_vertices(graph, 1)


def get_even_vertices(graph):
    """Given a networkx object, return names of the even vertices"""
    return _get_even_or_odd_vertices(graph, 0)


def get_shortest_paths_distances(graph, pairs, edge_weight_name):
    """Calculate shortest distance between each pair of vertices in a graph"""
    distances = {}
    for pair in pairs:
        distances[pair] = nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name)
    return distances


def create_complete_graph(pair_weights, flip_weights=True):
    """create a perfectly connected graph a list of vertex pairs and the distances between them."""
    g = nx.Graph()
    for k, v in pair_weights.items():
        wt_i = -v if flip_weights else v
        g.add_edge(k[0], k[1], attr_dict={'distance': v, 'weight': wt_i})
    return g


def dedupe_matching(matching):
    """Remove duplicates vertex pairs from the output of nx.algorithms.max_weight_matching"""
    matched_pairs_w_dupes = [tuple(sorted([k, v])) for k, v in matching.items()]
    return list(pd.unique(matched_pairs_w_dupes))


def add_augmenting_path_to_graph(graph, min_weight_pairs, edge_weight_name):
    """
    Add the min weight matching edges to the original graph
    Note the resulting graph could (and likely will) have edges that didn't exist on the original graph.  To get the
    true circuit, we must breakdown these augmented edges into the shortest path through the edges that do exist.
    """
    graph_aug = graph.copy()  # so we don't mess with the original graph
    for pair in min_weight_pairs:
        graph_aug.add_edge(pair[0],
                           pair[1],
                           attr_dict={'distance': nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name),
                                      'trail': 'augmented'}
                           )
    return graph_aug


def create_eulerian_circuit(graph_augmented, graph_original, start_node=None):
    """
    nx.eulerian_circuit only returns the order in which we hit each vertex.  It does not return the attributes of the
    edges needed to complete the circuit.  This is necessary for the postman problem where we to keep track of which
    edges have been covered already when multiple edges exist between two nodes.
    We also need to add the annotate the edges added to make the eulerian to follow the actual shortest path trails ( not
    the direct shortest path pairings between the odd nodes for which there might not be a direct trail)
    """
    euler_circuit = list(nx.eulerian_circuit(graph_augmented, source=start_node))

    assert len(graph_augmented.edges()) == len(euler_circuit), "graph and euler_circuit do not have equal number of edges."

    edge_data = graph_augmented.edges(data=True)

    for edge in euler_circuit:
        possible_edges = [e for e in edge_data if set([e[0], e[1]]) == set([edge[0], edge[1]])]

        if possible_edges[0][2]['trail'] == 'augmented':
            # find shortest path from odd node to odd node in original graph
            aug_path = nx.shortest_path(graph_original, edge[0], edge[1], weight='distance')
            # for each shortest path between odd nodes, add the shortest path through edges that actually exist to circuit
            for edge_aug in list(zip(aug_path[:-1], aug_path[1:])):
                # find edge with shortest distance (if there are two parallel edges btwn the same nodes)
                edge_aug_dict = graph_original[edge_aug[0]][edge_aug[1]]
                edge_aug_shortest = edge_aug_dict[min(edge_aug_dict.keys(), key=(lambda k: edge_aug_dict[k]['distance']))]
                edge_aug_shortest['augmented'] = True
                yield(edge_aug + (edge_aug_shortest,))
        else:
            yield(edge + (possible_edges[0][2],))
        edge_data.remove(possible_edges[0])


def cpp(edgelist_filename, nodelist_filename=None, start_node=None, edge_weight='distance'):
    """
    Solving the CPP from beginning (load network data) to end (finding optimal route).
    Can be run from command line with arguments from cpp.py, or from an interactive Python session (ex jupyter notebook)

    Args:
        edgelist_filename (str): filename of edgelist.  See cpp.py for more details
        start_node (str): name of starting node.  See cpp.py for more details

    Returns:
        list[tuple(str, str, dict)]: Each tuple is a direction (from one node to another) from the CPP solution route.
        The first element is the starting ("from") node.
        The second element is the end ("to") node.
        The third element is the dict of edge attributes for that edge.
    """
    el = read_edgelist(edgelist_filename)
    g = create_networkx_graph_from_edgelist(el)

    # get augmenting path for odd vertices
    odd_vertices = get_odd_vertices(g)
    odd_vertex_pairs = list(itertools.combinations(odd_vertices, 2))
    odd_vertex_pairs_shortest_paths = get_shortest_paths_distances(g, odd_vertex_pairs, edge_weight)
    g_odd_complete = create_complete_graph(odd_vertex_pairs_shortest_paths, flip_weights=True)

    # best solution using blossom algorithm
    odd_matching = dedupe_matching(nx.algorithms.max_weight_matching(g_odd_complete, True))

    # add the min weight matching edges to g
    g_aug = add_augmenting_path_to_graph(g, odd_matching, 'weight')

    # get eulerian circuit route.
    circuit = list(create_eulerian_circuit(g_aug, g, start_node))

    return circuit


