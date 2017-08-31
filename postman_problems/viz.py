import os
import glob
import imageio
import numpy as np
import graphviz as gv


def add_pos_node_attribute(graph, origin='bottomleft'):
    """
    Add node attribute 'pos' with X and Y coordinates to networkx graph so that we can the positions of each node to
    graphviz for plotting.  The origin for the X,Y plane is provided as some tools for grabbing coordinates from images
    use the topleft or the bottomleft.
    """
    ori = {
        'bottomleft': {'X': 1, 'Y': 1},
        'topleft': {'X': 1, 'Y': -1},
        'topright': {'X': -1, 'Y': -1},
        'bottomright': {'X': -1, 'Y': 1}
    }[origin]

    for node_id in graph.nodes():
        graph.node[node_id]['pos'] = "{},{}!".format(ori['X']*graph.node[node_id]['X'] / 100,
                                                     ori['Y']*graph.node[node_id]['Y'] / 100)
    return graph


def convert_networkx_graph_to_graphiz(graph, directed=False):
    """
    Convert a networkx Multigraph to a graphviz.dot.Graph
    This allows us to modify the graphviz graph programmatically in Python before we dump to dot format and plot.
    Note the Graphviz plot is created sequentially... It is hard to edit it after the edges and node attrs are written.
    """
    if directed:
        G = gv.Digraph(strict=False, graph_attr={'forcelabels': 'True'})
    else:
        G = gv.Graph(strict=False, graph_attr={'forcelabels': 'True'})

    for n in graph.nodes():
        n_attr = {k: str(v) for k, v in graph.node[n].items()}
        G.attr('node', n_attr)
        G.node(n, n)

    for e in graph.edges(keys=True):
        e_attr = {k: str(v) for k, v in graph[e[0]][e[1]][e[2]].items()}
        G.edge(e[0], e[1], **e_attr)

    return G


def make_circuit_graphviz(circuit, graph, filename='cpp_graph', format='svg', engine='neato'):
    """"
    Builds one graph
    TODO: consider making this a directed graph with edge labels specifying the order in which the edges should be
    traversed.
    """
    cnt = 1
    parallel_edge_cnt = {}
    for e in circuit:
        e_pair = frozenset([e[0], e[1]])
        # if an edge has been traversed already between e[0] and e[1]:
        if e_pair in parallel_edge_cnt:
            # if there are parallel edges not yet traversed, pick a new edge.
            if len(graph[e[0]][e[1]]) <= parallel_edge_cnt[e_pair]:
                parallel_edge_cnt[e_pair] += 1
                graph[e[0]][e[1]][parallel_edge_cnt[(e[0], e[1])]]['label'] = str(cnt)
            # if all parallel edges have been traversed, pick the shortest one
            else:
                min_parallel_edge_index = min(graph[e[0]][e[1]].keys(), key=lambda x: graph[e[0]][e[1]][x]['distance'])
                graph[e[0]][e[1]][min_parallel_edge_index]['label'] += ', ' + str(cnt)
        # if no edge between e[0] and e[1] has been traversed yet:
        else:
            parallel_edge_cnt[e_pair] = 0
            graph[e[0]][e[1]][parallel_edge_cnt[e_pair]]['label'] = str(cnt)
            graph[e[0]][e[1]][parallel_edge_cnt[e_pair]]['penwidth'] = 1
            graph[e[0]][e[1]][parallel_edge_cnt[e_pair]]['decorate'] = True
        graph[e[0]][e[1]][parallel_edge_cnt[e_pair]]['penwidth'] += 1



        cnt += 1

    graph_walked_gv = convert_networkx_graph_to_graphiz(graph, directed=False)
    graph_walked_gv.format = format
    graph_walked_gv.engine = engine
    graph_walked_gv.render(filename=filename, view=False)


def make_circuit_images(circuit, graph, path_plot, format='png', engine='neato'):
    """"
    Builds (in a hacky way) a sequence of plots that simulate the network growing according to the eulerian path.
    TODO: consider making this a directed graph with edge labels specifying the order in which the edges should be
    traversed.
    """
    graph_white = graph.copy()

    for e in graph_white.edges(keys=True):
        graph_white.node[e[0]]['color'] = 'white'
        graph_white.node[e[0]]['fontcolor'] = 'white'
        graph_white.node[e[1]]['color'] = 'white'
        graph_white.node[e[1]]['fontcolor'] = 'white'
        graph_white[e[0]][e[1]][e[2]]['color'] = 'white'

    cnt = 0
    parallel_edge_cnter = {}
    for e in circuit:
        # keeping track of when we need to add more edges to viz...parallel edges (or backtracks)
        if (e[0], e[1]) in parallel_edge_cnter:
            parallel_edge_cnter[(e[0], e[1])] += 1
        else:
            parallel_edge_cnter[(e[0], e[1])] = 0

        graph_white.node[e[0]]['color'] = 'black'
        graph_white.node[e[0]]['fontcolor'] = 'black'
        graph_white.node[e[1]]['color'] = 'black'
        graph_white.node[e[1]]['fontcolor'] = 'black'
        key = parallel_edge_cnter[(e[0], e[1])]

        graph_white[e[0]][e[1]][key]['color'] = 'black'  # make this smarter to use distance

        graph_walked_gv = convert_networkx_graph_to_graphiz(graph_white)

        graph_walked_gv.format = format
        graph_walked_gv.engine = engine

        graph_walked_gv.render(filename=path_plot + 'img' + str(cnt), view=False)
        cnt += 1


def make_circuit_video(image_path, movie_filename, fps=3):
    # sorting filenames in order
    filenames = glob.glob(image_path + 'img*.png')
    filenames_sort_indices = np.argsort([int(os.path.basename(filename).split('.')[0][3:]) for filename in filenames])
    filenames = [filenames[i] for i in filenames_sort_indices]

    # make movie
    with imageio.get_writer(movie_filename, mode='I', fps=fps) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
