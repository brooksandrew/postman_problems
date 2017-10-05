import pkg_resources
import logging
import string
import networkx as nx
from postman_problems.tests.utils import create_mock_csv_from_dataframe
from postman_problems.stats import calculate_postman_solution_stats
from postman_problems.solver import rpp, cpp


def create_star_graph(n_nodes=10, ring=True):
    """
    Create a star graph with the points connected by
    Args:
        n_nodes (int): number of nodes in graph (max 26)
        ring (Boolean): add ring around the border with low (distance=2) weights

    Returns:
        networkx MultiGraoh in the shape of a star

    """
    graph = nx.MultiGraph()
    node_names = list(string.ascii_lowercase)[:n_nodes]
    graph.add_star(node_names)
    nx.set_edge_attributes(graph, 10, 'distance')
    nx.set_edge_attributes(graph, 1, 'required')
    nx.set_edge_attributes(graph, 'solid', 'style')
    if ring:
        for e in list(zip(node_names[1:-1] + [node_names[1]], node_names[2:] + [node_names[-1]])):
            graph.add_edge(e[0], e[1], distance=2, required=0, style='dashed')
    return graph


def main():
    """Solve the RPP and save visualizations of the solution"""

    # PARAMS / DATA ---------------------------------------------------------------------

    # inputs
    START_NODE = 'a'
    N_NODES = 13

    # filepaths
    CPP_REQUIRED_SVG_FILENAME = pkg_resources.resource_filename('postman_problems',
                                                                'examples/star/output/cpp_graph_req')
    CPP_OPTIONAL_SVG_FILENAME = pkg_resources.resource_filename('postman_problems',
                                                                'examples/star/output/cpp_graph_opt')
    RPP_SVG_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/star/output/rpp_graph')
    RPP_BASE_SVG_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/star/output/base_rpp_graph')
    PNG_PATH = pkg_resources.resource_filename('postman_problems', 'examples/star/output/png/')
    RPP_GIF_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/star/output/rpp_graph.gif')

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # CREATE GRAPH ----------------------------------------------------------------------

    logger.info('Solve RPP')
    graph_base = create_star_graph(N_NODES)
    edgelist = nx.to_pandas_edgelist(graph_base, source='_node1', target='_node2')

    # SOLVE CPP -------------------------------------------------------------------------

    # with required edges only
    edgelist_file = create_mock_csv_from_dataframe(edgelist)
    circuit_cpp_req, graph_cpp_req = cpp(edgelist_file, start_node=START_NODE)
    logger.info('Print the CPP solution (required edges only):')
    for e in circuit_cpp_req:
        logger.info(e)

    # with required and optional edges as required
    edgelist_all_req = edgelist.copy()
    edgelist_all_req.drop(['required'], axis=1, inplace=True)
    edgelist_file = create_mock_csv_from_dataframe(edgelist_all_req)
    circuit_cpp_opt, graph_cpp_opt = cpp(edgelist_file, start_node=START_NODE)
    logger.info('Print the CPP solution (optional and required edges):')
    for e in circuit_cpp_opt:
        logger.info(e)

    # SOLVE RPP -------------------------------------------------------------------------

    edgelist_file = create_mock_csv_from_dataframe(edgelist)  # need to regenerate
    circuit_rpp, graph_rpp = rpp(edgelist_file, start_node=START_NODE)

    logger.info('Print the RPP solution:')
    for e in circuit_rpp:
        logger.info(e)

    logger.info('Solution summary stats:')
    for k, v in calculate_postman_solution_stats(circuit_rpp).items():
        logger.info(str(k) + ' : ' + str(v))

    # VIZ -------------------------------------------------------------------------------

    try:
        from postman_problems.viz import plot_circuit_graphviz, plot_graphviz, make_circuit_images, make_circuit_video

        logger.info('Creating single SVG of base graph')
        plot_graphviz(graph=graph_base,
                      filename=RPP_BASE_SVG_FILENAME,
                      edge_label_attr='distance',
                      format='svg',
                      engine='circo',
                      graph_attr={'label': 'Base Graph: Distances', 'labelloc': 't'}
                      )

        logger.info('Creating single SVG of CPP solution (required edges only)')
        plot_circuit_graphviz(circuit=circuit_cpp_req,
                              graph=graph_cpp_req,
                              filename=CPP_REQUIRED_SVG_FILENAME,
                              format='svg',
                              engine='circo',
                              graph_attr={
                                  'label': 'Base Graph: Chinese Postman Solution (required edges only)',
                                  'labelloc': 't'}
                              )

        logger.info('Creating single SVG of CPP solution (required & optional edges)')
        plot_circuit_graphviz(circuit=circuit_cpp_opt,
                              graph=graph_cpp_opt,
                              filename=CPP_OPTIONAL_SVG_FILENAME,
                              format='svg',
                              engine='circo',
                              graph_attr={'label': 'Base Graph: Chinese Postman Solution (required & optional edges)',
                                          'labelloc': 't'}
                              )

        logger.info('Creating single SVG of RPP solution')
        plot_circuit_graphviz(circuit=circuit_rpp,
                              graph=graph_rpp,
                              filename=RPP_SVG_FILENAME,
                              format='svg',
                              engine='circo',
                              graph_attr={'label': 'Base Graph: Rural Postman Solution', 'labelloc': 't'}
                              )

        logger.info('Creating PNG files for GIF')
        make_circuit_images(circuit=circuit_rpp,
                            graph=graph_rpp,
                            outfile_dir=PNG_PATH,
                            format='png',
                            engine='circo')

        logger.info('Creating GIF')
        make_circuit_video(infile_dir_images=PNG_PATH,
                           outfile_movie=RPP_GIF_FILENAME,
                           fps=1)

    except FileNotFoundError(OSError) as e:
        print(e)
        print("Sorry, looks like you don't have all the needed visualization dependencies.")


if __name__ == '__main__':
    main()
