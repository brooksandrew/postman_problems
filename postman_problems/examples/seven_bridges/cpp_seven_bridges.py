"""
Description:
    This example solves and visualizes the CPP on the network derived from the famous Seven Bridges of Konigsberg problem.
    See: https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg

    This example produces the following in `/output`.  The output is contained within this repo for convenience,
    and so I can embed the visualizations in the documentation.
      - an SVG of the optimal route with edges annotated by order
      - a GIF that animates the static images with the walk order of each edge
      - a directory of static PNGs needed to create the GIF
      - a dot graph representation (file) of the static network augmented with Eulerian circuit info.

Usage:
    The simplest way to run this example is at the command line with the code below.  To experiment within an
    interactive python environment using an interpreter (ex: Jupyter notebook), remove the `if __name__ == '__main__':`
    line, and you should be good to go.
    ```
    chinese_postman_seven_bridges
    ```
    or

    ```
    python postman_problems/examples/seven_bridges/cpp_seven_bridges.py
    ```
"""


import logging
import pkg_resources
from postman_problems.graph import cpp


def main():
    """Solve the CPP and save visualizations of the solution"""

    # PARAMS / DATA ---------------------------------------------------------------------

    # inputs
    EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/edgelist_seven_bridges.csv')
    START_NODE = 'D'

    # outputs
    PNG_PATH = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/png/')
    CPP_VIZ_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph')
    CPP_BASE_VIZ_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/base_cpp_graph')
    CPP_GIF_FILENAME = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph.gif')

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # SOLVE CPP -------------------------------------------------------------------------

    logger.info('Solve CPP')
    circuit, graph = cpp(edgelist_filename=EDGELIST, start_node=START_NODE)

    logger.info('Print the CPP solution:')
    for e in circuit:
        logger.info(e)

    # VIZ -------------------------------------------------------------------------------

    try:
        from postman_problems.viz import make_circuit_graphviz, make_circuit_images, make_circuit_video

        logger.info('Creating single SVG of base graph')
        base_graph_gv = make_circuit_graphviz(circuit=circuit,
                                              graph=graph,
                                              filename=CPP_BASE_VIZ_FILENAME,
                                              edge_label_attr='distance',
                                              format='svg',
                                              engine='circo')

        logger.info('Creating single SVG of CPP solution')
        graph_gv = make_circuit_graphviz(circuit=circuit,
                                         graph=graph,
                                         filename=CPP_VIZ_FILENAME,
                                         format='svg',
                                         engine='circo')

        logger.info('Creating PNG files for GIF')
        make_circuit_images(circuit=circuit,
                            graph=graph,
                            outfile_dir=PNG_PATH,
                            format='png',
                            engine='circo')

        logger.info('Creating GIF')
        video_message = make_circuit_video(infile_dir_images=PNG_PATH,
                                           outfile_movie=CPP_GIF_FILENAME,
                                           fps=0.5)

        logger.info(video_message)
        logger.info("and that's a wrap, checkout the output!")

    except FileNotFoundError(OSError) as e:
        print(e)
        print("Sorry, looks like you don't have all the needed visualization dependencies.")


if __name__ == '__main__':
    main()
