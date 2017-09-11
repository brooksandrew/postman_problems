import pandas as pd
import networkx as nx
from postman_problems.viz import add_node_attributes


# ###################
# PARAMETERS / DATA #
# ###################

GRAPH = nx.MultiGraph([
    ('a', 'b', {'id': 1, 'distance': 5}),
    ('a', 'c', {'id': 2, 'distance': 20}),
    ('b', 'c', {'id': 3, 'distance': 10}),
    ('c', 'd', {'id': 4, 'distance': 3}),
    ('d', 'b', {'id': 5, 'distance': 2})
])

NODE_ATTRIBUTES = pd.DataFrame({
    'id': ['a', 'b', 'c', 'd'],
    'attr_fruit': ['apple', 'banana', 'cherry', 'durian']
})


#########
# TESTS #
#########

def test_add_node_attributes():
    graph_node_attrs = add_node_attributes(GRAPH, NODE_ATTRIBUTES)
    assert set([n[1]['attr_fruit'] for n in graph_node_attrs.nodes(data=True)]) == \
           set(['apple', 'banana', 'cherry', 'durian'])
