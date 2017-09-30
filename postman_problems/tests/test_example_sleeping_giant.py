import math
import pkg_resources
import itertools
import pandas as pd
import networkx as nx
from postman_problems.viz import add_node_attributes
from postman_problems.graph import (
    read_edgelist, create_networkx_graph_from_edgelist, get_odd_nodes, get_shortest_paths_distances
)
from postman_problems.solver import rpp, cpp

# ###################
# PARAMETERS / DATA #
# ###################

EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
NODELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/nodelist_sleeping_giant.csv')
START_NODE = 'b_end_east'


#########
# TESTS #
#########

def test_read_sleeping_giant_edgelist():
    df = read_edgelist(EDGELIST, keep_optional=True)

    # check that our Sleeping Giant example dataset contains the correct fields and values
    assert ['node1', 'node2', 'trail', 'color', 'distance', 'estimate', 'required'] in df.columns.values
    assert math.isclose(df[df['required'] == 1]['distance'].sum(), 26.01)
    assert math.isclose(df['distance'].sum(), 30.48)

    df_req = read_edgelist(EDGELIST, keep_optional=False)
    assert math.isclose(df_req['distance'].sum(), 26.01)
    assert 'req' not in df_req.columns


def test_create_networkx_graph_from_edgelist():
    df = read_edgelist(EDGELIST, keep_optional=True)
    graph = create_networkx_graph_from_edgelist(df, edge_id='id')

    # check that our starting graph is created correctly
    assert isinstance(graph, nx.MultiGraph)
    assert len(graph.edges()) == 133
    assert len(graph.nodes()) == 78
    assert graph['b_end_east']['b_y'][0]['color'] == 'blue'
    assert graph['b_end_east']['b_y'][0]['trail'] == 'b'
    assert graph['b_end_east']['b_y'][0]['distance'] == 1.32

    # check that starting graph with required trails only is correct
    df_req = read_edgelist(EDGELIST, keep_optional=False)
    graph_req = create_networkx_graph_from_edgelist(df_req, edge_id='id')
    assert isinstance(graph_req, nx.MultiGraph)
    assert len(graph_req.edges()) == 121
    assert len(graph_req.nodes()) == 74


def test_add_node_attributes():
    # create objects for testing
    df = read_edgelist(EDGELIST)
    graph = create_networkx_graph_from_edgelist(df, edge_id='id')
    nodelist_df = pd.read_csv(NODELIST)
    graph_node_attrs = add_node_attributes(graph, nodelist_df)

    assert len(graph_node_attrs.nodes()) == 74

    # check that each node attribute has an X and Y coordinate
    for k, v in graph_node_attrs.nodes(data=True):
        assert 'X' in v
        assert 'Y' in v

    # spot check node attributes for first node
    node_data_from_graph = list(graph_node_attrs.nodes(data=True))

    node_names = [n[0] for n in node_data_from_graph]
    assert 'rs_end_north' in node_names

    key = node_names.index('rs_end_north')
    assert node_data_from_graph[key][1]['X'] == 1772
    assert node_data_from_graph[key][1]['Y'] == 172


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


def test_nodelist_edgelist_overlap():
    """
    Test that the nodelist and the edgelist contain the same node names.  If using X,Y coordinates for plotting and
    not all nodes have attributes, this could get messy.
    """
    eldf = read_edgelist(EDGELIST, keep_optional=True)
    nldf = pd.read_csv(NODELIST)
    edgelist_nodes = set(eldf['node1'].append(eldf['node2']))
    nodelist_nodes = set(nldf['id'])

    nodes_in_el_but_not_nl = edgelist_nodes - nodelist_nodes
    assert nodes_in_el_but_not_nl == set(), \
        "Warning: The following nodes are in the edgelist, but not the nodelist: {}".format(nodes_in_el_but_not_nl)

    nodes_in_nl_but_not_el = nodelist_nodes - edgelist_nodes
    assert nodes_in_nl_but_not_el == set(), \
        "Warning: The following nodes are in the nodelist, but not the edgelist: {}".format(nodes_in_nl_but_not_el)


def test_sleeping_giant_cpp_solution():
    cpp_solution, graph = cpp(edgelist_filename=EDGELIST, start_node=START_NODE)

    # make number of edges in solution is correct
    assert len(cpp_solution) == 155

    # make sure our total mileage is correct
    cpp_solution_distance = sum([edge[3]['distance'] for edge in cpp_solution])
    assert math.isclose(cpp_solution_distance, 33.25)

    # make sure our circuit begins and ends at the same place
    assert cpp_solution[0][0] == cpp_solution[-1][1] == START_NODE

    # make sure original graph is properly returned
    assert len(graph.edges()) == 121
    [e[2].get('augmented') for e in graph.edges(data=True)].count(True) == 35


def test_sleeping_giant_rpp_solution():
    rpp_solution, graph = rpp(edgelist_filename=EDGELIST, start_node=START_NODE)

    # make number of edges in solution is correct
    assert len(rpp_solution) == 151

    # make sure our total mileage is correct
    rpp_solution_distance = sum([edge[3]['distance'] for edge in rpp_solution])
    assert math.isclose(rpp_solution_distance, 32.12)

    # make sure our circuit begins and ends at the same place
    assert rpp_solution[0][0] == rpp_solution[-1][1] == START_NODE

    # make sure original graph is properly returned
    assert len(graph.edges()) == 133
    [e[3].get('augmented') for e in graph.edges(data=True, keys=True)].count(True) == 30

