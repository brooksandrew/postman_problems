import pkg_resources
from postman_problems.graph import create_networkx_graph_from_edgelist, cpp, read_edgelist
from postman_problems.viz import make_circuit_graphviz


EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sevenbridges/edgelist_seven_bridges.csv')


df = read_edgelist(EDGELIST)
graph = create_networkx_graph_from_edgelist(df)
circuit = cpp(EDGELIST, start_node='D')
make_circuit_graphviz(circuit, graph, format='svg', engine='dot')






