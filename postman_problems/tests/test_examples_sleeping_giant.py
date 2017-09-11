import math
import pkg_resources
import itertools
import warnings
import pandas as pd
import networkx as nx
from postman_problems.graph import (
    read_edgelist, create_networkx_graph_from_edgelist, get_odd_nodes, get_even_nodes, get_shortest_paths_distances,
    add_node_attributes, create_complete_graph, dedupe_matching, add_augmenting_path_to_graph, create_eulerian_circuit
)

# ###################
# PARAMETERS / DATA #
# ###################

EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
NODELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/nodelist_sleeping_giant.csv')


#########
# TESTS #
#########

def test_read_sleeping_giant_edgelist():
    df = read_edgelist(EDGELIST)

    # check that our Sleeping Giant example dataset contains the correct fields and values
    assert ['node1', 'node2', 'trail', 'color', 'distance', 'estimate'] in df.columns.values
    assert math.isclose(df['distance'].sum(), 25.76)


def test_create_networkx_graph_from_edgelist():
    df = read_edgelist(EDGELIST)
    graph = create_networkx_graph_from_edgelist(df, edge_id='id')

    # check that our starting graph is created correctly
    assert isinstance(graph, nx.MultiGraph)
    assert len(graph.edges()) == 119
    assert len(graph.nodes()) == 73
    assert graph['b_end_east']['b_y'][0]['color'] == 'blue'
    assert graph['b_end_east']['b_y'][0]['trail'] == 'b'
    assert graph['b_end_east']['b_y'][0]['distance'] == 1.32


def test_add_node_attributes():
    # create objects for testing
    df = read_edgelist(EDGELIST)
    graph = create_networkx_graph_from_edgelist(df, edge_id='id')
    nodelist_df = pd.read_csv(NODELIST)
    graph_node_attrs = add_node_attributes(graph, nodelist_df)

    assert len(graph_node_attrs.nodes()) == 73

    # check that each node attribute has an X and Y coordinate
    for k, v in graph_node_attrs.nodes(data=True):
        assert 'X' in v
        assert 'Y' in v

    # spot check node attributes for first node
    print(graph_node_attrs.nodes(data=True)[0][0])
    assert graph_node_attrs.nodes(data=True)[0][0] == 'rs_end_north'
    assert graph_node_attrs.nodes(data=True)[0][1]['X'] == 1772
    assert graph_node_attrs.nodes(data=True)[0][1]['Y'] == 172


def test_get_shortest_paths_distances():

    df = read_edgelist(EDGELIST)
    graph = create_networkx_graph_from_edgelist(df, edge_id='id')

    odd_nodes = get_odd_nodes(graph)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))

    # coarsely checking structure of `get_shortest_paths_distances` return value
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(graph, odd_node_pairs, 'distance')
    assert len(odd_node_pairs_shortest_paths) == 630
    assert type(odd_node_pairs_shortest_paths) == dict

    # check that each node name appears the same number of times in `get_shortest_paths_distances` return value
    node_names = list(itertools.chain(*[i[0] for i in odd_node_pairs_shortest_paths.items()]))
    assert set(pd.value_counts(node_names)) == set([35])
