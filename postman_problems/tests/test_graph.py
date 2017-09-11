
import itertools
import warnings
import pandas as pd
import networkx as nx
from postman_problems.graph import (
    read_edgelist, create_networkx_graph_from_edgelist, get_odd_nodes, get_even_nodes, get_shortest_paths_distances,
    create_complete_graph, dedupe_matching, add_augmenting_path_to_graph, create_eulerian_circuit
)
from postman_problems.tests.utils import create_mock_csv_from_dataframe


# ###################
# PARAMETERS / DATA #
# ###################

NODE_PAIRS = {('a', 'b'): 2, ('b', 'c'): 5, ('c', 'd'): 10}
MATCHING = {'a': 'b', 'd': 'c', 'b': 'a', 'c': 'd'}
GRAPH = nx.MultiGraph([
    ('a', 'b', {'id': 1, 'distance': 5}),
    ('a', 'c', {'id': 2, 'distance': 20}),
    ('b', 'c', {'id': 3, 'distance': 10}),
    ('c', 'd', {'id': 4, 'distance': 3}),
    ('d', 'b', {'id': 5, 'distance': 2})
])
EDGELIST_DF_W_ID = pd.DataFrame({
    'node1': ['a', 'a', 'b', 'c', 'd'],
    'node2': ['b', 'c', 'c', 'd', 'b'],
    'distance': [5, 20, 10, 3, 2],
    'id': [1, 2, 3, 4, 5],
}, columns=['node1', 'node2', 'distance', 'id'])
EDGELIST_DF = EDGELIST_DF_W_ID.drop('id', axis=1)
NODE_ATTRIBUTES = pd.DataFrame({
    'id': ['a', 'b', 'c', 'd'],
    'attr_fruit': ['apple', 'banana', 'cherry', 'durian']
})


#########
# TESTS #
#########

def test_read_edgelist():
    EDGELIST_CSV = create_mock_csv_from_dataframe(EDGELIST_DF)
    df = read_edgelist(EDGELIST_CSV)
    assert df.shape == (5, 3)
    assert set(df.columns) == set(['distance', 'node1', 'node2'])


def test_read_edgelist_w_ids():
    EDGELIST_CSV = create_mock_csv_from_dataframe(EDGELIST_DF_W_ID)
    with warnings.catch_warnings(record=True) as w:
        df = read_edgelist(EDGELIST_CSV)

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
    assert set([e[2]['distance'] for e in graph.edges(data=True)]) == set([5, 20, 10, 2, 3])


def test_create_networkx_graph_from_edgelist_w_ids():
    with warnings.catch_warnings(record=True) as w:
        graph = create_networkx_graph_from_edgelist(EDGELIST_DF_W_ID, edge_id='id')

        # make sure correct warning was given
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert 'already an edge attribute in `edgelist`' in str(w[-1].message)

    # make sure our graph is as it should be
    _test_graph_structure(graph)


def test_create_networkx_graph_from_edgelist_w_ids():
    graph = create_networkx_graph_from_edgelist(EDGELIST_DF, edge_id='id')
    _test_graph_structure(graph)  # make sure our graph is as it should be


def test_get_degree_nodes():
    # check that even + odd == total
    assert len(get_odd_nodes(GRAPH)) + len(get_even_nodes(GRAPH)) == len(GRAPH.nodes())
    # check that there is no overlap between odd and even
    assert set(get_odd_nodes(GRAPH)).intersection(get_even_nodes(GRAPH)) == set()


def test_get_shortest_paths_distances():
    odd_nodes = get_odd_nodes(GRAPH)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))
    # coarsely checking structure of `get_shortest_paths_distances` return value
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(GRAPH, odd_node_pairs, 'distance')
    assert len(odd_node_pairs_shortest_paths) == 1
    assert type(odd_node_pairs_shortest_paths) == dict
    assert odd_node_pairs_shortest_paths[('b', 'c')] == 5


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


def test_add_augmenting_path_to_graph():
    graph_aug = add_augmenting_path_to_graph(GRAPH, [('b', 'c')], 'distance')
    assert len(graph_aug.edges()) == 6
    assert sum([e[2]['distance'] for e in graph_aug.edges(data=True)]) == 45
    assert [set([e[0], e[1]]) for e in graph_aug.edges(data=True)].count(set(['b', 'c'])) == 2


def test_create_eulerian_circuit():
    graph_aug = add_augmenting_path_to_graph(GRAPH, [('b', 'c')], 'distance')
    circuit = list(create_eulerian_circuit(graph_aug, GRAPH, 'a'))
    assert len(circuit) == 7
    assert sum([e[2]['distance'] for e in circuit]) == 45
    assert circuit[0][0] == 'a'
    assert circuit[-1][1] == 'a'
    assert [e[2]['id'] for e in circuit] == [2, 4, 5, 3, 4, 5, 1]



