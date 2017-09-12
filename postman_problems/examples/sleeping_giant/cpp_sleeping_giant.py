"""
Description:
    This example solves and visualizes the CPP on the network derived from the Sleeping Giant State Park trail map.

    This example produces the following in `/output`.  The output is contained within this repo for convenience,
    and so I can embed the visualizations in the documentation throughout.
      - an SVG of the optimal route with edges annotated by order
      - a GIF that demonstrates the
      - a directory of static PNGs needed to create the GIF
      - a dot graph representation (file) of the static network augmented with Eulerian circuit info.

Usage:
    The simplest way to run this example is at the command line with the code below.  To experiment within an
    interactive python environment using an interpreter (ex, Jupyter notebook), remove the `if __name__ == '__main__':`
    line, and you should be good to go.
        ```
        python postman_problems/examples/sleeping_giant/cpp_sleeping_giant.py
        ````
        or using the chinese_postman entry_point:
        ```
        chinese_postman --edgelist postman_problems/examples/sleeping_giant/edgelist_sleeping_giant.csv
        ```
        or skip right to the chase with the pre-parameterized entry point for Sleeping Giant.
        ```
        chinese_postman_sleeping_giant
        ```

    To run just the CPP optimization (not the viz) from the command line with different parameters, for example
    starting from a different node, try:
        ```
        python postman_problems/chinese_postman.py \
        --edgelist_filename 'postman_problems/examples/sleeping_giant/edgelist_sleeping_giant.csv' \
        --start_node 'rs_end_south'
        ```
"""

import logging
import pkg_resources
import pandas as pd
from postman_problems.graph import cpp
from postman_problems.viz import (
    add_pos_node_attribute, add_node_attributes, make_circuit_graphviz, make_circuit_images, make_circuit_video
)


def main():
    """Solve the CPP and save visualizations of the solution"""

    # PARAMS / DATA -------------------------------------

    # inputs
    EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
    NODELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/nodelist_sleeping_giant.csv')
    START_NODE = "b_end_east"

    # outputs
    NODE_ATTR = {'shape': 'point', 'color': 'black', 'width': '0.1'}
    PNG_PATH = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/png/')
    CPP_SVG_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/cpp_graph')
    CPP_GIF_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/cpp_graph.gif')

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # SOLVE CPP -----------------------------------------

    logger.info('Solve CPP')
    circuit, graph = cpp(EDGELIST, START_NODE)

    logger.info('Print the CPP solution:')
    for e in circuit:
        logger.info(e)

    # VIZ -----------------------------------------------

    logger.info('Add node attributes to graph')
    nodelist_df = pd.read_csv(NODELIST)
    graph = add_node_attributes(graph, nodelist_df)  # add attributes
    graph = add_pos_node_attribute(graph, origin='bottomleft')  # add X,Y positions in format for graphviz

    logger.info('Creating single SVG of CPP solution')
    graph_gv = make_circuit_graphviz(circuit=circuit,
                                     graph=graph,
                                     filename=CPP_SVG_FILENAME,
                                     format='svg',
                                     engine='neato',
                                     node_attr=NODE_ATTR)

    logger.info('Creating PNG files for GIF')
    images_message = make_circuit_images(circuit=circuit,
                                         graph=graph,
                                         outfile_dir=PNG_PATH,
                                         format='png',
                                         engine='neato',
                                         node_attr=NODE_ATTR)
    logger.info(images_message)

    logger.info('Creating GIF')
    video_message = make_circuit_video(infile_dir_images=PNG_PATH,
                                       outfile_movie=CPP_GIF_FILENAME,
                                       fps=2)
    logger.info(video_message)
    logger.info("and that's a wrap, checkout the output!")


if __name__ == '__main__':
    main()
