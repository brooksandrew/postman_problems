"""

"""

import logging
import pkg_resources
import pandas as pd
from postman_problems.solver import rpp
from postman_problems.stats import calculate_postman_solution_stats


def main():
    """Solve the RPP and save visualizations of the solution"""

    # PARAMS / DATA ---------------------------------------------------------------------

    # inputs
    EDGELIST = pkg_resources.resource_filename('postman_problems',
                                               'examples/sleeping_giant/edgelist_sleeping_giant.csv')
    NODELIST = pkg_resources.resource_filename('postman_problems',
                                               'examples/sleeping_giant/nodelist_sleeping_giant.csv')
    START_NODE = "b_end_east"

    # outputs
    GRAPH_ATTR = {'dpi': '65'}
    EDGE_ATTR = {'fontsize': '20'}
    NODE_ATTR = {'shape': 'point', 'color': 'black', 'width': '0.1', 'fixedsize': 'true'}

    PNG_PATH = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/png/')
    RPP_SVG_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/rpp_graph')
    RPP_GIF_FILENAME = pkg_resources.resource_filename('postman_problems',
                                                       'examples/sleeping_giant/output/rpp_graph.gif')

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # SOLVE RPP -------------------------------------------------------------------------

    logger.info('Solve RPP')
    circuit, graph = rpp(EDGELIST, START_NODE)

    logger.info('Print the RPP solution:')
    for e in circuit:
        logger.info(e)

    logger.info('Solution summary stats:')
    for k, v in calculate_postman_solution_stats(circuit).items():
        logger.info(str(k) + ' : ' + str(v))

    # VIZ -------------------------------------------------------------------------------

    try:
        from postman_problems.viz import (
            add_pos_node_attribute, add_node_attributes, plot_circuit_graphviz, make_circuit_images, make_circuit_video
        )

        logger.info('Add node attributes to graph')
        nodelist_df = pd.read_csv(NODELIST)
        graph = add_node_attributes(graph, nodelist_df)  # add attributes
        graph = add_pos_node_attribute(graph, origin='topleft')  # add X,Y positions in format for graphviz

        logger.info('Add style edge attribute to make optional edges dotted')
        for e in graph.edges(data=True, keys=True):
            graph[e[0]][e[1]][e[2]]['style'] = 'solid' if graph[e[0]][e[1]][e[2]]['required'] else 'dashed'

        logger.info('Creating single SVG of RPP solution')
        plot_circuit_graphviz(circuit=circuit,
                              graph=graph,
                              filename=RPP_SVG_FILENAME,
                              format='svg',
                              engine='neato',
                              graph_attr=GRAPH_ATTR,
                              edge_attr=EDGE_ATTR,
                              node_attr=NODE_ATTR
                              )

        logger.info('Creating PNG files for GIF')
        images_message = make_circuit_images(circuit=circuit,
                                             graph=graph,
                                             outfile_dir=PNG_PATH,
                                             format='png',
                                             engine='neato',
                                             graph_attr=GRAPH_ATTR,
                                             edge_attr=EDGE_ATTR,
                                             node_attr=NODE_ATTR)
        logger.info(images_message)

        logger.info('Creating GIF')
        video_message = make_circuit_video(infile_dir_images=PNG_PATH,
                                           outfile_movie=RPP_GIF_FILENAME,
                                           fps=3)
        logger.info(video_message)
        logger.info("and that's a wrap, checkout the output!")

    except FileNotFoundError(OSError) as e:
        print(e)
        print("Sorry, looks like you don't have all the needed visualization dependencies.")


if __name__ == '__main__':
    main()
