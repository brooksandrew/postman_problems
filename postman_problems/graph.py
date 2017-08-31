import itertools
import pandas as pd
import networkx as nx
from postman_problems.viz import add_pos_node_attribute


def read_edgelist(edgelist_filename):
    """Read an edgelist table into a pandas dataframe"""
    el = pd.read_csv(edgelist_filename)
    el = el.dropna()
    return el


def create_networkx_graph_from_edgelist(edgelist, edge_attributes={'weight': 'distance'}):
    """
    Create a networkx object from an edgelist (pandas dataframe)
    The first two columns are treated as source and target vertex names.
    The following columns are treated as edge attributes.
    The :edge_attributes: parameter is a dict that will rename columns as necessary (networkx expects an edge attribute
    named weight)
    """
    g = nx.MultiGraph()
    g.add_nodes_from(list(set(edgelist.ix[:, 0].append(edgelist.ix[:, 0]))))
    sum_dist = sum(pd.to_numeric(edgelist[edge_attributes['weight']]))
    for row in edgelist.iterrows():
        edge_attr_dict = row[1][2:].to_dict()
        edge_attr_dict['weight'] = edge_attr_dict[edge_attributes['weight']]
        edge_attr_dict['weight_flipped'] = -edge_attr_dict[edge_attributes['weight']]
        g.add_edge(row[1][0], row[1][1], attr_dict=edge_attr_dict)
    return g


def add_node_attributes(g, nodelist):
    """Adds node attributes to graph"""
    for i, row in nodelist.iterrows():
        g.node[row['id']] = row.to_dict()
    return g


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


def find_min_weight_matching_dumb(pairs, weights):
    """
    Dumb function for finding pairings of odd vertex.  Could be smarter w updates/more iterations.
    Or implement Edmonds Blossum algorithm.
    """
    paths = list(zip(pairs, weights))
    paths.sort(key=lambda x: x[1])
    connected_vertices = []
    matched_pairs = []
    for edge in paths:
        if (edge[0][0] not in connected_vertices) & (edge[0][1] not in connected_vertices):
            connected_vertices.append(edge[0][0])
            connected_vertices.append(edge[0][1])
            matched_pairs.append(edge[0])
    return matched_pairs


def create_complete_graph(pair_weights, flip_weights=True):
    """create a perfectly connected graph using a vertex pair and """
    g = nx.Graph()
    sum_dist = sum(pair_weights.values())
    for k, v in pair_weights.items():
        wt_i = sum_dist - v if flip_weights else v
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
    graph_aug = graph.copy()
    for pair in min_weight_pairs:
        graph_aug.add_edge(pair[0], pair[1], attr_dict={'distance': nx.dijkstra_path_length(graph, pair[0], pair[1], weight=edge_weight_name),
                                                        'trail': 'augmented'})
    return graph_aug


def create_eulerian_circuit(graph_augmented, graph_original, starting_node=None):
    """
    nx.eulerian_circuit only returns the order in which we hit each vertex.  It does not return the attributes of the
    edges needed to complete the circuit.  This is necessary for the postman problem where we to keep track of which
    edges have been covered already when multiple edges exist between two nodes.
    We also need to add the annotate the edges added to make the eulerian to follow the actual shortest path trails ( not
    the direct shortest path pairings between the odd nodes for which there might not be a direct trail)
    """
    euler_circuit = list(nx.eulerian_circuit(graph_augmented, source=starting_node))

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


def circuit_to_graph(circuit):
    """
    Not currently using this....
    """
    graph = nx.DiGraph(strict=False)
    for e in circuit:
        graph.add_edge(e[0], e[1], e[2])
    return graph


def cpp(config):
    """Chinese Postman Problem"""
    el = read_edgelist(config['data']['edgelist'])
    g = create_networkx_graph_from_edgelist(el)

    # get augmenting path for odd vertices
    odd_vertices = get_odd_vertices(g)
    odd_vertex_pairs = list(itertools.combinations(odd_vertices, 2))
    odd_vertex_pairs_shortest_paths = get_shortest_paths_distances(g, odd_vertex_pairs, 'weight')
    g_odd_complete = create_complete_graph(odd_vertex_pairs_shortest_paths, flip_weights=True)

    # best solution using blossom algorithm
    odd_matching = dedupe_matching(nx.algorithms.max_weight_matching(g_odd_complete, True))

    # add the min weight matching edges to g
    g_aug = add_augmenting_path_to_graph(g, odd_matching, 'weight')

    # get eulerian circuit route.
    circuit = list(create_eulerian_circuit(g_aug, g, config['data']['starting_node']))

    return circuit


