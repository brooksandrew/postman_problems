import pytest
import networkx as nx
import pandas as pd
from postman_problems.tests.utils import create_mock_csv_from_dataframe


# ---------------------------------------------------------------------------------------
# Configuration for slow tests
# ---------------------------------------------------------------------------------------

def pytest_addoption(parser):
    """
    Grabbed from:
    https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
    """
    parser.addoption('--runslow', action='store_true', default=False, help='run slow tests')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--runslow'):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason='need --runslow option to run')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)

# ---------------------------------------------------------------------------------------
# Graph objects shared between tests
# ---------------------------------------------------------------------------------------


#   -------------------------------------------------------------------------------------
#   Graph 1: Simple graph.  Required edges only.  CPP == RPP
#   -------------------------------------------------------------------------------------

@pytest.fixture(scope='session', autouse=True)
def GRAPH_1():
    return nx.MultiGraph([
        ('a', 'b', {'id': 1, 'distance': 5}),
        ('a', 'c', {'id': 2, 'distance': 20}),
        ('b', 'c', {'id': 3, 'distance': 10}),
        ('c', 'd', {'id': 4, 'distance': 3}),
        ('d', 'b', {'id': 5, 'distance': 2})
    ])


@pytest.fixture(scope='session', autouse=True)
def GRAPH_1_EDGELIST_DF_W_ID():
    return pd.DataFrame({
        'node1': ['a', 'a', 'b', 'c', 'd'],
        'node2': ['b', 'c', 'c', 'd', 'b'],
        'distance': [5, 20, 10, 3, 2],
        'id': [1, 2, 3, 4, 5]
    }, columns=['node1', 'node2', 'distance', 'id'])


@pytest.fixture(scope='function', autouse=True, )
def GRAPH_1_EDGELIST_DF(GRAPH_1_EDGELIST_DF_W_ID):
    return GRAPH_1_EDGELIST_DF_W_ID.drop('id', axis=1)


@pytest.fixture(scope='function', autouse=True)
def GRAPH_1_EDGELIST_CSV(GRAPH_1_EDGELIST_DF):
    return create_mock_csv_from_dataframe(GRAPH_1_EDGELIST_DF)


@pytest.fixture(scope='function', autouse=True)
def GRAPH_1_EDGELIST_W_ID_CSV(GRAPH_1_EDGELIST_DF_W_ID):
    return create_mock_csv_from_dataframe(GRAPH_1_EDGELIST_DF_W_ID)


@pytest.fixture(scope='session', autouse=True)
def GRAPH_1_NODE_ATTRIBUTES():
    return pd.DataFrame({
        'id': ['a', 'b', 'c', 'd'],
        'attr_fruit': ['apple', 'banana', 'cherry', 'durian']
    })


@pytest.fixture(scope='session', autouse=True)
def GRAPH_1_CIRCUIT_CPP():
    return [
        ('a', 'b', 0, {'distance': 5, 'id': 0}),
        ('b', 'd', 0, {'distance': 2, 'augmented': True, 'id': 4}),
        ('d', 'c', 0, {'distance': 3, 'augmented': True, 'id': 3}),
        ('c', 'b', 0, {'distance': 10, 'id': 2}),
        ('b', 'd', 0, {'distance': 2, 'id': 4}),
        ('d', 'c', 0, {'distance': 3, 'id': 3}),
        ('c', 'a', 0, {'distance': 20, 'id': 1})
    ]


#   -------------------------------------------------------------------------------------
#   Graph 2: Star graph.  Short optional edges on border
#   -------------------------------------------------------------------------------------


@pytest.fixture(scope='session', autouse=True)
def GRAPH_2():
    return nx.MultiGraph([
        ('a', 'b', {'distance': 20, 'required': 1}),
        ('a', 'c', {'distance': 25, 'required': 1}),
        ('a', 'd', {'distance': 30, 'required': 1}),
        ('a', 'e', {'distance': 35, 'required': 1}),
        ('b', 'c', {'distance': 2, 'required': 0}),
        ('c', 'd', {'distance': 3, 'required': 0}),
        ('d', 'e', {'distance': 4, 'required': 0}),
        ('e', 'b', {'distance': 6, 'required': 0})
    ])


@pytest.fixture(scope='session', autouse=True)
def GRAPH_2_EDGELIST_CSV(GRAPH_2):
    edgelist = nx.to_pandas_edgelist(GRAPH_2, source='_node1', target='_node2')
    return create_mock_csv_from_dataframe(edgelist)


@pytest.fixture(scope='session', autouse=True)
def GRAPH_2_CIRCUIT_RPP():
    return [
        ('a', 'c', 0, {'distance': 25, 'id': 4, 'required': 1}),
        ('c', 'b', 0, {'distance': 2, 'id': 6, 'augmented': True, 'required': 0}),
        ('b', 'a', 0, {'distance': 20, 'id': 3, 'required': 1}),
        ('a', 'e', 0, {'distance': 35, 'id': 5, 'required': 1}),
        ('e', 'd', 0, {'distance': 4, 'id': 2, 'augmented': True, 'required': 0}),
        ('d', 'a', 0, {'distance': 30, 'id': 0, 'required': 1})
    ]


#   -------------------------------------------------------------------------------------
#   Graph 3: Star graph.  Graph with > 1 connected component when optional edges are removed
#   -------------------------------------------------------------------------------------


@pytest.fixture(scope='session', autouse=True)
def GRAPH_3():
    return nx.MultiGraph([
        ('a', 'b', {'distance': 20, 'required': 1}),
        ('a', 'c', {'distance': 25, 'required': 1}),
        ('a', 'd', {'distance': 30, 'required': 1}),
        ('a', 'e', {'distance': 35, 'required': 1}),
        ('b', 'c', {'distance': 2, 'required': 0}),
        ('c', 'd', {'distance': 3, 'required': 0}),
        ('d', 'e', {'distance': 4, 'required': 0}),
        ('e', 'b', {'distance': 6, 'required': 0}),
        ('b', 'f', {'distance': 7, 'required': 0}),
        ('f', 'g', {'distance': 8, 'required': 1})
    ])


@pytest.fixture(scope='session', autouse=True)
def GRAPH_3_EDGELIST_CSV(GRAPH_3):
    edgelist = nx.to_pandas_edgelist(GRAPH_3, source='_node1', target='_node2')
    return create_mock_csv_from_dataframe(edgelist)