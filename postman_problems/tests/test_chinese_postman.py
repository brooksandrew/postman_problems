import math
import pkg_resources
import itertools
import pandas as pd
from postman_problems.graph import (
    cpp, read_edgelist, create_networkx_graph_from_edgelist, get_odd_nodes, get_even_nodes, get_shortest_paths_distances
)


# PARAMETERS / DATA

# TODO: figure out how to reference this more stably w pkg_resources or package_data.
#EDGELIST = 'postman_problems/tests/edgelist_sleeping_giant.csv'  # works
EDGELIST = pkg_resources('examples', 'sleepinggiant/edgelist_sleeping_giant.csv') # might not work
START_NODE = 'b_end_east'


# TESTS

def test_read_sleeping_giant_edgelist():
    df = read_edgelist(EDGELIST)

    # check that our Sleeping Giant example dataset contains the correct fields and values
    assert ['node1', 'node2', 'trail', 'distance', 'estimate'] in df.columns.values
    assert math.isclose(df['distance'].sum(), 25.76)


def test_get_degree_nodes():
    df = read_edgelist(EDGELIST)
    g = create_networkx_graph_from_edgelist(df)

    # check that even + odd == total
    assert len(get_odd_nodes(g)) + len(get_even_nodes(g)) == len(g.nodes())

    # check that there is no overlap between odd and even
    assert set(get_odd_nodes(g)).intersection(get_even_nodes(g)) == set()


def test_sleeping_giant_cpp_solution():
    cpp_solution = cpp(edgelist_filename=EDGELIST, start_node=START_NODE)

    # make number of edges in solution is correct
    assert len(cpp_solution) == 154

    # make sure our total mileage is correct
    cpp_solution_distance = sum([edge[2]['distance'] for edge in cpp_solution])
    assert math.isclose(cpp_solution_distance, 33.59)

    # make sure our circuit begins and ends at the same place
    assert cpp_solution[0][0] == cpp_solution[-1][1] == START_NODE


def test_get_shortest_paths_distances():

    # redefining necessary objects.  TODO: these could be fixtures.
    df = read_edgelist(EDGELIST)
    g = create_networkx_graph_from_edgelist(df)
    odd_nodes = get_odd_nodes(g)
    odd_node_pairs = list(itertools.combinations(odd_nodes, 2))

    # coarsely checking structure of `get_shortest_paths_distances` return value
    odd_node_pairs_shortest_paths = get_shortest_paths_distances(g, odd_node_pairs, 'distance')
    assert len(odd_node_pairs_shortest_paths) == 630
    assert type(odd_node_pairs_shortest_paths) == dict

    # check that each node name appears the same number of times in `get_shortest_paths_distances` return value
    node_names = list(itertools.chain(*[i[0] for i in odd_node_pairs_shortest_paths.items()]))
    assert set(pd.value_counts(node_names)) == set([35])








