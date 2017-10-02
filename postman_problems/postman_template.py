import os
import argparse
import logging
from postman_problems.solver import cpp, rpp
from postman_problems.viz import plot_circuit_graphviz, make_circuit_video, make_circuit_images
from postman_problems.stats import calculate_postman_solution_stats


def get_args():
    """
    Returns:
        argparse.Namespace: parsed arguments from the user
    """
    parser = argparse.ArgumentParser(description='Arguments to the Chinese Postman Problem solver')

    # ---------------------------------------------------------------
    # CPP optimization
    # ---------------------------------------------------------------

    parser.add_argument('--edgelist',
                        required=True,
                        type=str,
                        help='Filename of edgelist.'
                             'Expected to be comma delimited text file readable with pandas.read_csv'
                             'The first two columns should be the "from" and "to" node names.'
                             'Additional columns can be provided for edge attributes.'
                             'The first row should be the edge attribute names.')

    parser.add_argument('--nodelist',
                        required=False,
                        type=str,
                        default=None,
                        help='Filename of node attributes (optional).'
                             'Expected to be comma delimited text file readable with pandas.read_csv'
                             'The first column should be the node name.'
                             'Additional columns should be used to provide node attributes.'
                             'The first row should be the node attribute names.')

    parser.add_argument('--start_node',
                        required=False,
                        type=str,
                        default=None,
                        help='Node to start the CPP solution from (optional).'
                             'If not provided, a starting node will be selected at random.')

    parser.add_argument('--edge_weight',
                        required=False,
                        type=str,
                        default='distance',
                        help='Edge attribute used to specify the distance between nodes (optional).'
                             'Default is "distance".')

    # ---------------------------------------------------------------
    # CPP viz
    # ---------------------------------------------------------------

    parser.add_argument('--viz',
                        action='store_true',
                        help='Write out the static image of the CPP solution using graphviz?')

    parser.add_argument('--animation',
                        action='store_true',
                        help='Write out an animation (GIF) of the CPP solution using a series of static graphviz images')

    parser.add_argument('--viz_engine',
                        required=False,
                        type=str,
                        default='dot',
                        help='graphviz engine to use for viz layout: "dot", "neato", "fdp", etc) of solution static viz')

    parser.add_argument('--animation_engine',
                        required=False,
                        type=str,
                        default='dot',
                        help='graphviz engine to use for viz layout: "dot", "neato", "fdp", etc) of solution animation '
                             'viz')

    parser.add_argument('--animation_format',
                        required=False,
                        type=str,
                        default='png',
                        help='File type to use when writing out animation of CPP solution viz using graphviz.')

    parser.add_argument('--fps',
                        required=False,
                        type=float,
                        default=3,
                        help='Frames per second to use for CPP solution animation.')

    parser.add_argument('--viz_filename',
                        required=False,
                        type=str,
                        default='cpp_graph.svg',
                        help='Filename to write static (single) viz of CPP solution to.  Do not include the file type '
                             'suffix. This is added with the `format` argument.')

    parser.add_argument('--animation_filename',
                        required=False,
                        type=str,
                        default='cpp_graph.gif',
                        help='Filename to write animation (GIF) of CPP solution viz to.')

    parser.add_argument('--animation_images_dir',
                        required=False,
                        type=str,
                        default=None,
                        help='Directory where the series of static visualizations will be produced that get stitched '
                             'into the animation.')

    # Grabbing viz file format from the filename
    args = parser.parse_args()
    args.viz_format = os.path.basename(args.viz_filename).split('.')[-1]

    return args


def generic_postman(postman_type):
    """
    Runs the CPP or RPP algorithm, prints solution, saves visualizations to filesystem

    Args:
        postman_type (str): "rural" or "chinese"
    """

    if postman_type == 'rural':
        postman_algo = rpp
    elif postman_type == 'chinese':
        postman_algo = cpp

    # get args
    args = get_args()

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info('Solving the {} postman problem..'.format(postman_type))
    circuit, graph = postman_algo(edgelist_filename=args.edgelist,
                                       start_node=args.start_node,
                                       edge_weight=args.edge_weight)

    logger.info('Solution:')
    for edge in circuit:
        logger.info(edge)

    logger.info('Solution summary stats:')
    for k, v in calculate_postman_solution_stats(circuit).items():
        logger.info(str(k) + ' : ' + str(v))

    if args.viz:
        logger.info('Creating single image of {} postman solution...'.format(postman_type))
        message_static = plot_circuit_graphviz(circuit=circuit,
                                               graph=graph,
                                               filename=args.viz_filename,
                                               format=args.viz_format,
                                               engine=args.viz_engine)
        logger.info(message_static)

    if args.animation:
        animation_images_dir = args.animation_images_dir if args.animation_images_dir else os.path.join(
            os.path.dirname(args.animation_filename), 'img')

        logger.info('Creating individual files for animation...')
        message_images = make_circuit_images(circuit=circuit,
                                             graph=graph,
                                             outfile_dir=animation_images_dir,
                                             format=args.animation_format,
                                             engine=args.animation_engine)
        logger.info(message_images)

        logger.info('Creating animation...')
        message_animation = make_circuit_video(infile_dir_images=animation_images_dir,
                                               outfile_movie=args.animation_filename,
                                               fps=args.fps,
                                               format=args.animation_format)
        logger.info(message_animation)

