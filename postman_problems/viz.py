import os
import glob
import imageio
import tqdm
import numpy as np
import graphviz as gv
from collections import defaultdict


def add_node_attributes(graph, nodelist):
    """
    Adds node attributes to graph.  Only used for visualization.

    Args:
        graph (networkx graph): graph you want to add node attributes to
        nodelist (pandas dataframe): containing node attributes.
            Expects a column named 'id' specifying the node names from `graph`.
            Other columns should specify desired node attributes.
            First row should include attribute names.

    Returns:
        networkx graph: original `graph` augmented w node attributes
    """
    for i, row in nodelist.iterrows():
        graph.node[row['id']] = row.to_dict()
    return graph


def add_pos_node_attribute(graph, origin='bottomleft'):
    """
    Add node attribute 'pos' with X and Y coordinates to networkx graph so that we can the positions of each node to
    graphviz for plotting.  The origin for the X,Y plane is provided as some tools for grabbing coordinates from images
    use the topleft or the bottomleft.

    Args:
        graph (networkx graph): graph to "pos" node attribute to.  `graph` already should X, Y node attributes.
        origin (str): How to treat origin for X, Y.  One of: 'bottomleft', 'topleft', 'topright', 'bottomright'

    Returns:
        networkx graph with the node attributes added to graph
    """

    ori = {
        'bottomleft': {'X': 1, 'Y': 1},
        'topleft': {'X': 1, 'Y': -1},
        'topright': {'X': -1, 'Y': -1},
        'bottomright': {'X': -1, 'Y': 1}
    }[origin]

    for node_id in graph.nodes():
        try:
            # dividing by arbitrary number to make pos appear as required type: double
            graph.node[node_id]['pos'] = "{},{}!".format(ori['X']*graph.node[node_id]['X']/100,
                                                         ori['Y']*graph.node[node_id]['Y']/100)
        except KeyError as e:
            print(e)
            print('No X, Y coordinates found for node: {}'.format(node_id))
    return graph


def prepare_networkx_graph_for_transformation_to_graphviz(circuit, graph, edge_label_attr=None):
    """
    Augment the original graph with information from the CPP solution (`circuit`) to get graph ready for conversion
    to a graphviz object.  We hardcode node and edge parameters that graphviz knows how to handle such as penwidth,
    decorate, pos, etc.  It is much easier to manipulate attributes in networkx than to try and add them after the
    graphviz object is created.

    Args:
        circuit (list[tuple]): CPP solution from `graph.cpp`
        graph (networkx graph): original graph
        edge_label_attr (str) optional name of graph edge attribute to use for label. Default None uses index from circuit.

    Returns:
        networkx graph: `graph` augmented with information from `circuit`
    """
    edge_cnter = defaultdict(lambda: 0)
    for i, e in enumerate(circuit):

        # edge attributes
        eid = e[2]['id']
        edge_id2key = {v['id']: k for k, v in graph[e[0]][e[1]].items()}
        key = edge_id2key[eid]

        if eid not in edge_cnter:
            graph[e[0]][e[1]][key]['label'] = str(graph[e[0]][e[1]][key][edge_label_attr]) if edge_label_attr else str(i)
            graph[e[0]][e[1]][key]['penwidth'] = 1
            graph[e[0]][e[1]][key]['decorate'] = 'true'
        else:
            if edge_label_attr is None:
                graph[e[0]][e[1]][key]['label'] += ', ' + str(i)
            graph[e[0]][e[1]][key]['penwidth'] += 3
        edge_cnter[eid] += 1

    return graph


def convert_networkx_graph_to_graphiz(graph, directed=False):
    """
    Convert a networkx Multigraph to a graphviz.dot.Graph
    This allows us to modify the graphviz graph programmatically in Python before we dump to dot format and plot.
    Note the Graphviz plot is created sequentially... It is hard to edit it after the edges and node attrs are written.

    Args:
        graph (networkx graph): networkx graph to be converted to dot notation
        directed (boolean): is `graph` directed... more specifically, do we want the returned graph to be directed?

    Returns:
        graphviz.dot.Graph: conversion of `graph` to a graphviz dot object.
    """
    if directed:
        G = gv.Digraph()
    else:
        G = gv.Graph()

    # add nodes and their attributes to graphviz object
    for n in graph.nodes():
        n_attr = {k: str(v) for k, v in graph.node[n].items()}
        G.attr('node', n_attr)
        G.node(n, n)

    # add edges and their attributes to graphviz object
    for e in graph.edges(keys=True):
        e_attr = {k: str(v) for k, v in graph[e[0]][e[1]][e[2]].items()}
        G.edge(e[0], e[1], **e_attr)

    return G


def make_circuit_graphviz(circuit, graph, filename=None, format='svg', engine='dot', edge_label_attr=None,
                          graph_attr={'strict': 'false', 'forcelabels': 'true'}, node_attr=None, edge_attr=None):
    """
    Builds single graphviz graph with CPP solution.
    Wrapper around functions:
     - prepare_networkx_graph_for_transformation_to_graphviz
     - convert_networkx_graph_to_graphiz

    Args:
        circuit (list[tuple]): solution of the CPP (result from graph.cpp function
        graph (networkx graph): original graph augmented with ``
        filename (str): filename of viz output (leave off the file extension... this is appended from `format`)
        format (str): 'svg', 'png`, etc
        engine (str) : which graphviz engine to use: 'dot', 'neato'. 'circo', etc
        edge_label_attr (str) optional name of graph edge attribute to use for label. Default None uses index from circuit.
        graph_attr (dict): of graphviz graph level attributes.
        node_attr (dict): of graphviz node attributes to pass to each node
        edge_attr (dict): of graphviz edge attributes to pass to each edge.

    Returns:
        graphviz.Graph or graphviz.DirectedGraph with enriched route and plotting data.
        Writes a visualization to disk if filename is provided.
    """
    graph = prepare_networkx_graph_for_transformation_to_graphviz(circuit, graph, edge_label_attr)

    # convert networkx object to graphviz object
    graph_gv = convert_networkx_graph_to_graphiz(graph, directed=False)
    graph_gv.engine = engine
    graph_gv.format = format

    # setting graph options.
    if graph_attr:
        for k, v in graph_attr.items():
            graph_gv.graph_attr[k] = v

    # setting node options (these will override graph attributes if there is overlap)
    if node_attr:
        for k, v in node_attr.items():
            graph_gv.node_attr[k] = v

    # setting edge options (these will override graph attributes if there is overlap)
    if edge_attr:
        for k, v in edge_attr.items():
            graph_gv.edge_attr[k] = v

    # write to disk
    if filename:
        graph_gv.render(filename=filename, view=False)

    return graph_gv


def make_circuit_images(circuit, graph, outfile_dir, format='png', engine='neato',
                        graph_attr={'strict': 'false', 'forcelabels': 'true'}, node_attr=None, edge_attr=None):
    """
    Builds (in a hacky way) a sequence of plots that simulate the network growing according to the eulerian path.
    TODO: fix bug where edge labels populate with each direction (multiple walk) as soon as the first one comes up.

    Args:
        circuit (list[tuple]): solution of the CPP (result from graph.cpp function
        graph (networkx graph):
        outfile_dir (str): path to where a series of images named like img[X].[format] will be saved.
        format (str): 'svg', 'png`, etc
        engine: which graphviz engine to use: 'dot', 'neato'. 'circo', etc
        graph_attr (dict): of graphviz graph level attributes.
        node_attr (dict): of graphviz node attributes to pass to each node
        edge_attr (dict): of graphviz edge attributes to pass to each edge.

    Returns:
        No return value.  Writes a viz to disk for each instruction in the CPP.
    """
    graph_white = prepare_networkx_graph_for_transformation_to_graphviz(circuit, graph.copy())

    # Start w a blank (OK, opaque) canvas
    for e in graph_white.edges(keys=True):
        graph_white.node[e[0]]['color'] = graph_white.node[e[1]]['color'] = '#eeeeee'
        graph_white[e[0]][e[1]][e[2]]['color'] = '#eeeeee'
        graph_white[e[0]][e[1]][e[2]]['label'] = ''

    # Now let's start adding some color to it, one edge at a time:
    for i, e in enumerate(tqdm.tqdm(circuit)):

        # adding node colors
        eid = e[2]['id']
        graph_white.node[e[0]]['color'] = 'black'
        graph_white.node[e[1]]['color'] = 'red'  # will get overwritten at next step

        # adding edge colors and attributes
        edge_id2key = {v['id']: k for k, v in graph_white[e[0]][e[1]].items()}
        key = edge_id2key[eid]
        graph_white[e[0]][e[1]][key]['color'] = graph[e[0]][e[1]][key]['color'] if 'color' in graph[e[0]][e[1]][key] else 'red'

        png_filename = os.path.join(outfile_dir, 'img' + str(i))
        graph_gv = make_circuit_graphviz(circuit[0:i+1], graph_white, png_filename, format, engine, None, graph_attr, node_attr, edge_attr)

        graph_white[e[0]][e[1]][key]['color'] = 'black'  # set walked edge back to black

    return 'Images created in {}'.format(os.path.dirname(png_filename))


def make_circuit_video(infile_dir_images, outfile_movie, fps=3, format='png'):
    """
    Create a movie that visualizes the CPP solution from a series of static images.
    Args:
        infile_dir_images (str): path to list of images named like `img[X].png`.  These are produced from make_circuit_images
        outfile_movie (str): filename of created movie/gif (output)
        fps (int): frames per second for movie
        format (str): image format (png, jpeg, etc) used to generate images in named like img[X].[format].

    Returns:
        No return value.  Writes a movie/gif to disk
    """
    # sorting filenames in order
    filenames = glob.glob(os.path.join(infile_dir_images, 'img*.%s' % format))
    filenames_sort_indices = np.argsort([int(os.path.basename(filename).split('.')[0][3:]) for filename in filenames])
    filenames = [filenames[i] for i in filenames_sort_indices]

    # make movie
    with imageio.get_writer(outfile_movie, mode='I', fps=fps) as writer:
        for filename in tqdm.tqdm(filenames):
            image = imageio.imread(filename)
            writer.append_data(image)
    return 'Movie written to {}'.format(outfile_movie)
