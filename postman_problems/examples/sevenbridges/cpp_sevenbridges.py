import itertools
import pkg_resources
import networkx as nx
import pandas as pd

EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sevenbridges/edgelist_seven_bridges.csv')


df = pd.read_csv(EDGELIST)
g = create_networkx_graph_from_edgelist()






