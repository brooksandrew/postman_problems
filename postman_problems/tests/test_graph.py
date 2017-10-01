import collections
import itertools
import warnings

import networkx as nx
import pytest
from postman_problems.graph import (
    read_edgelist, create_networkx_graph_from_edgelist, get_odd_nodes, get_even_nodes, get_shortest_paths_distances,
    create_complete_graph, dedupe_matching, add_augmenting_path_to_graph, create_eulerian_circuit,
    assert_graph_is_connected, create_required_graph
)


# ###################
# PARAMETERS / DATA #
# ###################

NODE_PAIRS = {('a', 'b'): 2, ('b', 'c'): 5, ('c', 'd'): 10}
MATCHING = {'a': 'b', 'd': 'c', 'b': 'a', 'c': 'd'}


#########
# TESTS #
#########

def test_read_edgelist(GRAPH_1_EDGELIST_CSV):
    df = read_edgelist(GRAPH_1_EDGELIST_CSV)
    assert df.shape == (5, 3)
    assert set(df.columns) == set(['distance', 'node1', 'node2'])


def test_read_edgelist_w_ids(GRAPH_1_EDGELIST_W_ID_CSV):
    with warnings.catch_warnings(record=True) as w:
        df = read_edgelist(GRAPH_1_EDGELIST_W_ID_CSV)

        # make sure correct warning was given
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "Edgelist contains field named 'id'" in str(w[-1].message)

    assert df.shape == (5, 4)
    assert set(df.columns) == set(['distance', 'node1', 'node2', 'id'])


def _test_graph_structure(graph):
    assert len(graph.edges()) == 5
    assert len(graph.nodes()) == 4
    assert graph['a']['b'][0]['distance'] == 5
    assert set([e[3]['distance'] for e in graph.edges(data=True, keys=True)]) == set([5, 20, 10, 2, 3])


def test_create_networkx_graph_from_edgelist_w_ids_warning(GRAPH_1_EDGELIST_DF_W_ID):
    with warnings.catch_warnings(record=True) as w:
        graph = create_networkx_graph_from_edgelist(GRAPH_1_EDGELIST_DF_W_ID, edge_id='id')

        # make sure correct warning was given
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert 'already an edge attribute in `edgelist`' in str(w[-1].message)

    # make sure our graph is as it should be
    _test_graph_structure(graph)


def test_create_networkx_graph_from_edgelist_w_ids(GRAPH_1_EDGELIST_DF):
    graph = create_networkx_graph_from_edgelist(GRAPH_1_EDGELIST_DF, edge_id='id')
    _test_graph_structure(graph)  # make sure our graph is as it should be


def test_get_degree_nodes(GRAPH_1):
    # check that even + odd == total
    assert len(get_odd_nodes(GRAPH_1)) + len(get_even_nodes(GRAPH_1)) == len(GRAPH_1.nodes())
    # check that there is no overlap between odd and even
    assert set(get_odd_nodes(GRAPH_1)).intersection(get_even_nodes(GRAPH_1)) == set()


def test_get_shortest_paths_distances(GRAPH_1):
    odd_nodes = get_odd_nodes(GRAPH_1)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))

    # coarsely checking structure of `get_shortest_paths_distances` return value
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(GRAPH_1, odd_node_pairs, 'distance')
    assert len(odd_node_pairs_shortest_paths) == 1
    assert type(odd_node_pairs_shortest_paths) == dict
    bc_key = ('b', 'c') if ('b', 'c') in odd_node_pairs_shortest_paths else ('c', 'b')  # tuple keys are unordered
    assert odd_node_pairs_shortest_paths[bc_key] == 5


def test_create_complete_graph():
    # with flipped weights
    graph_complete = create_complete_graph(NODE_PAIRS, flip_weights=True)
    assert len(graph_complete.edges()) == 3
    assert set([e[2]['distance'] for e in graph_complete.edges(data=True)]) == set([2, 5, 10])
    assert set([e[2]['weight'] for e in graph_complete.edges(data=True)]) == set([-2, -5, -10])
    # without flipped weights
    graph_complete_noflip = create_complete_graph(NODE_PAIRS, flip_weights=False)
    assert len(graph_complete_noflip.edges()) == 3
    assert set([e[2]['distance'] for e in graph_complete_noflip.edges(data=True)]) == set([2, 5, 10])
    assert set([e[2]['weight'] for e in graph_complete_noflip.edges(data=True)]) == set([2, 5, 10])


def test_dedupe_matching():
    deduped_edges = [set(edge) for edge in dedupe_matching(MATCHING)]
    assert set(['b', 'a']) in deduped_edges
    assert set(['c', 'd']) in deduped_edges
    assert len(deduped_edges) == 2


def test_add_augmenting_path_to_graph(GRAPH_1):
    graph_aug = add_augmenting_path_to_graph(GRAPH_1, [('b', 'c')], 'distance')
    assert len(graph_aug.edges()) == 6
    assert sum([e[3]['distance'] for e in graph_aug.edges(data=True, keys=True)]) == 45
    assert [set([e[0], e[1]]) for e in graph_aug.edges(data=True)].count(set(['b', 'c'])) == 2


def test_create_eulerian_circuit(GRAPH_1):
    graph_aug = add_augmenting_path_to_graph(GRAPH_1, [('b', 'c')], 'distance')
    circuit = list(create_eulerian_circuit(graph_aug, GRAPH_1, 'a'))
    assert len(circuit) == 7
    assert sum([e[3]['distance'] for e in circuit]) == 45
    assert circuit[0][0] == 'a'
    assert circuit[-1][1] == 'a'
    assert collections.Counter([e[3]['id'] for e in circuit]) == collections.Counter({4: 2, 5: 2, 2: 1, 3: 1, 1: 1})


def test_check_graph_is_connected(GRAPH_1):
    assert assert_graph_is_connected(GRAPH_1)  # check that a connected graph is deemed as such

    GRAPH_2_COMP = GRAPH_1.copy()
    GRAPH_2_COMP.add_edge('e', 'f')
    with pytest.raises(AssertionError):
        assert_graph_is_connected(GRAPH_2_COMP)  # check that unconnected graph raises assertion


def test_create_required_graph(GRAPH_1):
    GRAPH_1_FULL = GRAPH_1.copy()
    nx.set_edge_attributes(GRAPH_1_FULL, 1, 'required')
    GRAPH_1_FULL['b']['d'][0]['required'] = 0
    GRAPH_1_FULL['c']['d'][0]['required'] = False  # testing 0 and False values for 'required'

    GRAPH_1_REQ = create_required_graph(GRAPH_1_FULL)
    assert set(GRAPH_1_REQ.nodes()) == set(['a', 'b', 'c'])
    assert set(GRAPH_1.nodes()) == set(['a', 'b', 'c', 'd'])
    assert len(GRAPH_1_REQ.edges()) == 3
    assert len(GRAPH_1.edges()) == 5


