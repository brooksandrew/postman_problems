import pkg_resources
from postman_problems.graph import create_networkx_graph_from_edgelist, cpp, read_edgelist, add_node_attributes
from postman_problems.viz import add_pos_node_attribute, make_circuit_graphviz


EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleepinggiant/edgelist_sleeping_giant.csv')
NODELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleepinggiant/nodelist_sleeping_giant.csv')

df = read_edgelist(EDGELIST)
graph = create_networkx_graph_from_edgelist(df)
nodelist = read_edgelist(NODELIST)
graph = add_node_attributes(graph, nodelist)
graph = add_pos_node_attribute(graph, origin='bottomleft')

circuit = cpp(EDGELIST, start_node='b_end_east')
make_circuit_graphviz(circuit, graph, format='svg', engine='dot')