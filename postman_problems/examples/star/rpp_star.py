import pkg_resources
import logging
import networkx as nx
from postman_problems.tests.utils import create_mock_csv_from_dataframe
from postman_problems.graph import rpp, cpp


def create_star_graph(n_nodes=10, ring=True):
    """
    Create a star graph with the points connected by
    Args:
        n_nodes (int): number of nodes in graph
        ring (Boolean): add ring around the border with low (distance=2) weights

    Returns:
        networkx graph in the shape of a star

    """
    graph = nx.MultiGraph()
    graph.add_star(range(n_nodes))
    nx.set_edge_attributes(graph, 10, 'distance')
    nx.set_edge_attributes(graph, 1, 'required')
    if ring:
        for e in list(zip(range(1, n_nodes), range(2, n_nodes+1))):
            graph.add_edge(e[0], e[1], distance=2, required=0)
    return graph


def main():
    """Solve the RPP and save visualizations of the solution"""

    # PARAMS / DATA ---------------------------------------------------------------------

    # inputs
    START_NODE = 0
    N_NODES = 10

    PNG_PATH = pkg_resources.resource_filename('postman_problems', 'examples/star/output/png/')
    RPP_SVG_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/star/output/rpp_graph')
    RPP_GIF_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/star/output/rpp_graph.gif')

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # SOLVE RPP -------------------------------------------------------------------------

    logger.info('Solve RPP')
    graph = create_star_graph(N_NODES)
    edgelist = nx.to_pandas_edgelist(graph, source='_node1', target='_node2')
    edgelist_file = create_mock_csv_from_dataframe(edgelist)

    circuit, graph = rpp(edgelist_file, start_node=START_NODE)

    logger.info('Print the RPP solution:')
    for e in circuit:
        logger.info(e)

    # VIZ -------------------------------------------------------------------------------

    try:
        from postman_problems.viz import make_circuit_graphviz, make_circuit_images, make_circuit_video

        logger.info('Creating single SVG of RPP solution')
        graph_gv = make_circuit_graphviz(circuit=circuit,
                                         graph=graph,
                                         filename=RPP_SVG_FILENAME,
                                         format='svg',
                                         engine='fdp'
                                         )
    except FileNotFoundError(OSError) as e:
        print(e)
        print("Sorry, looks like you don't have all the needed visualization dependencies.")


if __name__ == '__main__':
    main()