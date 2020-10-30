#   File Created 10/19/2020
#   Author: Jack Connor <jconnor@baaqmd.gov>

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import statistics as stats
from shapely.geometry import Polygon
from graph import strongly_connected_comp_splitter, shortest_paths_between_components, find_minimum_weight_edges_to_connect_components, create_rpp_edgelist
from compassbearing import calculate_initial_compass_bearing
from postman_problems.tests.utils import create_mock_csv_from_dataframe
import postman_problems.shortest_path_mod as spm

def create_inner_and_outer_graph(directory, InnerFileName, OuterFileName):
    """
    Reads in csv files with coordinates that define inner and outer polygons;
    Obtains NetworkX street graphs defined by these polygons.
    Args:
        directory (str): directory to look for csv files
        InnerFileName (str): Name of file containing coordinates defining inner polygon
        OuterFileName (str): Name of file containing coordinates defining outer polygon
    Returns:
        inner_g (NetworkX DiGraph): graph of street network contained by inner polygon
        outer_g (NetworkX DiGraph): graph of street network contained by outer polygon
    """

    InnerFilePath = directory + InnerFileName
    OuterFilePath = directory + OuterFileName

    inner_coord_df = pd.read_csv(InnerFilePath, index_col=0)
    outer_coord_df = pd.read_csv(OuterFilePath, index_col=0)

    inner_coordinates = []
    outer_coordinates = []
    i = 0
    for x in inner_coord_df['Longitude']:
        inner_coordinates += [[x, inner_coord_df.iloc[i][0]]]
        i += 1
    inner_coordinates += [inner_coordinates[0]]
    i = 0
    for x in outer_coord_df['Longitude']:
        outer_coordinates += [[x, outer_coord_df.iloc[i][0]]]
        i += 1
    outer_coordinates += [outer_coordinates[0]]

    inner_poly = Polygon(inner_coordinates)
    inner_g = ox.graph_from_polygon(inner_poly, network_type = 'drive')

    outer_poly = Polygon(outer_coordinates)
    outer_g = ox.graph_from_polygon(outer_poly, network_type = 'drive')

    return inner_g, outer_g

def create_turn_weight_edge_attr(graph, length_weight='length', normalization_coefficient=1):
    """
    add dictionary of turn weights to attributes for each edge
    Args:
        graph (NetworkX Graph): input graph with lat/lon attributes on nodes
        length_weight (str): edge attribute used for edge length
        normalization_coefficient (float): coefficient used to weight turn_weights relative to lengths
    Returns:
        NetworkX Graph with turn weight dictionary added to each edge.
        An edge's turn weight dictionary is keyed by possible predecessor edges.
    """
    length_min, length_max, length_median, length_mean, length_stdev = generate_turn_weight_normalization_parameters(graph, length_weight=length_weight)
    graph_copy=graph.copy()

    #e_prim is edge that turn attributes are added to, and e_pred is predecessor edge
    for e_prim in graph.edges(keys=True):
        for e_pred in graph.edges():
            if e_prim[0] == e_pred[1]:
                turn_start = e_pred[0]
                turn_middle = e_prim[0]
                turn_end = e_prim[1]

                key = e_prim[2]

                #create turn weights
                turn_start_lon = graph.nodes(data=True)[turn_start]['x']
                turn_middle_lon = graph.nodes(data=True)[turn_middle]['x']
                turn_end_lon = graph.nodes(data=True)[turn_end]['x']

                turn_start_lat = graph.nodes(data=True)[turn_start]['y']
                turn_middle_lat = graph.nodes(data=True)[turn_middle]['y']
                turn_end_lat = graph.nodes(data=True)[turn_end]['y']

                comp1_bearing = calculate_initial_compass_bearing((turn_start_lat, turn_start_lon), (turn_middle_lat, turn_middle_lon))
                comp2_bearing = calculate_initial_compass_bearing((turn_middle_lat, turn_middle_lon), (turn_end_lat, turn_end_lon))
                turn_angle = comp2_bearing-comp1_bearing
                if turn_angle < 0:
                    turn_angle = 360 + turn_angle
                if (turn_angle >= 315 and turn_angle <= 360) or (turn_angle >= 0 and turn_angle < 45):
                    turn_weight = 0
                elif turn_angle >= 45 and turn_angle < 135:
                    turn_weight = 1
                elif turn_angle >= 225 and turn_angle < 315:
                    turn_weight = 2
                else:
                    turn_weight = 4
                #create turn_length
                turn_length = turn_weight*length_max*normalization_coefficient

                #add turn_length attribute
                if 'turn_length' not in graph_copy[e_prim[0]][e_prim[1]][key]:
                    graph_copy[e_prim[0]][e_prim[1]][key]['turn_length'] = {e_pred[0] : turn_length}
                elif e_pred[0] not in graph_copy[e_prim[0]][e_prim[1]][key]['turn_length']:
                    graph_copy[e_prim[0]][e_prim[1]][key]['turn_length'][e_pred[0]] = turn_length
    return(graph_copy)

def generate_turn_weight_normalization_parameters(graph, length_weight='length'):
    """
    Calculate edge length statistics that can be used to normalize turn weights.
    Args:
        graph (NetworkX Graph): network that turn weight parameters are being added to
        length_weight (str): edge attribute for length weights
    Returns:
        tuple of floats: (
            length_min: minimum edge length
            length_max: maximum edge length
            length_median: median edge length
            length_mean: mean of edge lengths
            length_stdev: standard deviation of edge lengths
            )
    """
    
    new_graph = graph.copy()
    
    #investigate edge lengths
    length_list = []
    for e in graph.edges(data=True):
        if 'turn' not in e[2]:
            length_list += [e[2][length_weight]]
    length_min = min(length_list)
    length_max = max(length_list)
    length_median = stats.median(length_list)
    length_mean = stats.mean(length_list)
    length_stdev = stats.stdev(length_list)
    return length_min, length_max, length_median, length_mean, length_stdev

def turn_weight_function_length(v, u, e, pred_node):
    """
    Weight function used in modified version of Dijkstra path algorithm.
    Weight is calculated as the sum of edge length weight and turn length weight (turn length weight keyed by predecessor node)
    This version of the function takes edge lengths keyed with 'length'
    Args:
        v (var): edge start node
        u (var): edge end node
        e (dict): edge attribute dictionary with keys
        pred_node (var): predecessor node
    Returns:
        calculated edge weight (float)
    """
    if pred_node == None:
        weight = e[0]['length']
    else:
        weight = e[0]['length'] + e[0]['turn_length'][pred_node]
    return(weight)

def turn_weight_function_distance(v, u, e, pred_node):
    """
    Weight function used in modified version of Dijkstra path algorithm.
    Weight is calculated as the sum of edge length weight and turn length weight (turn length weight keyed by predecessor node)
    This version of the function takes edge lengths keyed with 'distance'
    Args:
        v (var): edge start node
        u (var): edge end node
        e (dict): edge attribute dictionary with keys
        pred_node (var): predecessor node
    Returns:
        calculated edge weight (float)
    """
    if pred_node == None:
        weight = e[0]['distance']
    else:
        weight = e[0]['distance'] + e[0]['turn_length'][pred_node]
    return(weight)

def determine_and_remove_extraneous_reverse_edges(graph):
    """
    Goes through strongly connected components and removes any reverse edge that is not required for strong connectivity.
    Args:
        graph (NetworkX DiGraph): initial graph of required street network
    Returns:
        NetworkX DiGraph with extraneous reverse edges removed 
    """

    # determine reversible edge list
    rev_edges = []
    for e in graph.edges():
        edge = set([e[0], e[1]])
        if graph.has_edge(e[1], e[0]) and edge not in rev_edges:
            rev_edges += [edge]

    # iterate through each strongly connected component. iterate through edges. remove edge through copy of subgraph. check if copy is still strongly connected.
    # if copy is still strongly connected, remove edge from graph
    modified_graph = graph.copy()
    for i, comp in enumerate([graph.subgraph(c).copy() for c in nx.strongly_connected_components(graph)]):
        comp_copy = comp.copy()
        for e in comp.edges():
            if {e[0], e[1]} in rev_edges:
                comp_copy_copy = comp_copy.copy()
                comp_copy_copy.remove_edge(e[0], e[1])
                if nx.algorithms.components.is_strongly_connected(comp_copy_copy):
                    comp_copy.remove_edge(e[0], e[1])
                    modified_graph.remove_edge(e[0], e[1])
                    rev_edges.remove({e[0], e[1]})

    print('\nInner Graph with Extraneous Reversible Edges Removed')

    return(modified_graph)

def simple_network_plotter(graph):
    """
    Plots a street network graph with node location attributes keyed as 'x' and 'y'
    Args:
        graph (NetworkX Graph): graph of street network to be plotted
    Returns:
        Shows figure with street network plotted
    """

    fig_1, ax_1 = plt.subplots()
    pos = {k: (graph.nodes[k].get('x'), graph.nodes[k].get('y')) for k in graph.nodes()}
    nx.draw_networkx_edges(graph, pos, ax = ax_1)
    ax_1.set_xlim(left = min([pos[node][0] for node in graph.nodes()]), right = max([pos[node][0] for node in graph.nodes()]))
    ax_1.set_ylim(bottom = min([pos[node][1] for node in graph.nodes()]), top = max([pos[node][1] for node in graph.nodes()]))
    plt.show()

    return

def strong_connector(inner_g, outer_g, edge_weight='length'):
    """
    Splits inner_g into strongly connected components
    Uses outer_g to connect strongly split graph into a strongly connected graph
    Args:
        inner_g (NetworkX DiGraph): inner graph of required edges
        outer_g (NetworkX DiGraph): complete street network graph containing all required and optional edges
        edge_weight (str): edge_weight used in strongly_connected_comp_splitter
    Returns:
        inner_g_strongly_connected (NetworkX MultiDiGraph): inner graph with additional edges to strongly connect
        all strongly connected components
    """

    inner_g_strongly_split = strongly_connected_comp_splitter(graph=inner_g, edge_weight=edge_weight)

    if nx.algorithms.components.is_strongly_connected(inner_g_strongly_split): 
        print('\nInner graph is strongly connected without adding connector edges')
        inner_g_strongly_connected = inner_g_strongly_split.copy()
    else:
        dfsp = shortest_paths_between_components(inner_g_strongly_split)
        connector_edges = find_minimum_weight_edges_to_connect_components(dfsp=dfsp, graph=outer_g, edge_weight=turn_weight_function_length, top=20)
        #'distance' attribute associated with connector edge contains turn_lengths within the connector path. turn_length dictionary for first edge in path needs to be added.
        for e in connector_edges:
            if 'name' in outer_g[e[2]['path'][0]][e[2]['path'][1]][0]:
                s_e_n = outer_g[e[2]['path'][0]][e[2]['path'][1]][0]['name']
            elif 'junction' in outer_g[e[2]['path'][0]][e[2]['path'][1]][0]:
                s_e_n = 'junction_' + outer_g[e[2]['path'][0]][e[2]['path'][1]][0]['junction']
            else:
                s_e_n = 'unlabeled'
            path = e[2]['path']
            turn_length = outer_g[path[0]][path[1]][0]['turn_length']
            attr = {
                    'start_node' : e[0],
                    'end_node' : e[1],
                    'distance' : e[2]['distance'],
                    'length': e[2]['length'],
                    'path' : path,
                    'turn_length' : turn_length,
                    'start_edge_name' : s_e_n,
                    'required' : 1,
                    'connector' : True,
                    }
            inner_g_strongly_split.add_edge(e[0], e[1], **attr)
        print("\nConnector edges added")
        inner_g_strongly_split_copy = inner_g_strongly_split.copy()
        for e in inner_g_strongly_split.edges(data=True):
            if 'connector' in e[2] and e[2].get('connector'):
                for pair in list(zip(e[2]['path'][:-1], e[2]['path'][1:])):
                    #add granular connector edges to graph
                    inner_g_strongly_split_copy.add_edge(pair[0], pair[1], granular=True, granular_type='connector')
                #add granular connector nodes to graph
                for n in e[2]['path']:
                    inner_g_strongly_split_copy.add_node(n, y=outer_g.nodes[n]['y'], x=outer_g.nodes[n]['x'])
        inner_g_strongly_connected = inner_g_strongly_split_copy
        if nx.algorithms.components.is_strongly_connected(inner_g_strongly_connected):
            print('Inner graph is strongly connected after adding connector edges')
        else:
            print('Inner graph is NOT strongly connected after adding connector edges')
    return inner_g_strongly_connected

def strongly_connected_graph_plotter(inner_g_strongly_connected):
    """
    Plots graph color coded by strongly connected components and connector edges
    Args:
        inner_g_strongly_connected (NetworkX MultiDiGraph): street network graph generated by strong_connector
    Returns:
        figure with color coded plot
        print statements describing figure
    """

    fig_1, ax_1 = plt.subplots()
    pos = {k: (inner_g_strongly_connected.nodes[k].get('x'), inner_g_strongly_connected.nodes[k].get('y')) for k in inner_g_strongly_connected.nodes()}

    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
    comp_max = 0
    for e in inner_g_strongly_connected.edges(data=True):
        if 'comp' in e[2] and e[2].get('comp') > comp_max:
            comp_max = e[2].get('comp')
    for e in inner_g_strongly_connected.edges(data=True):
        if 'comp' not in e[2]:
            e[2]['comp'] = comp_max + 1
    comp_max += 1
    comps = list(range(0, comp_max+1))

    print()
    i=0
    for comp in comps:
        #excludes contracted connector edges (labeled as 'connector') so that only granular edges are plotted
        el = [e for e in inner_g_strongly_connected.edges(data=True) if e[2].get('comp') == comp and 'connector' not in e[2]]
        #el = [e for e in inner_g_strongly_connected.edges(data=True) if e[2].get('comp') == comp]
        nx.draw_networkx_edges(inner_g_strongly_connected, pos, edgelist=el, ax = ax_1, edge_color=colors[i])
        if comp != comp_max:
            print('Comp {} drawn'.format(comp) + ' in ' + colors[i])
        else:
            if len(comps)>2:
                print('Connector edges drawn in ' + colors[i])
        i+=1
    ax_1.set_xlim(left = min([pos[node][0] for node in inner_g_strongly_connected.nodes()]), right = max([pos[node][0] for node in inner_g_strongly_connected.nodes()]))
    ax_1.set_ylim(bottom = min([pos[node][1] for node in inner_g_strongly_connected.nodes()]), top = max([pos[node][1] for node in inner_g_strongly_connected.nodes()]))
    plt.show()

    return

def pick_western_most_start_node(req_g):
    """
    Sets START_NODE equal to western-most node
    Args:
        req_g (NetworkX Graph): graph of street network containing all required edges
    Returns:
        START_NODE (var): wester-most node
    """
    x = list(req_g.nodes(data=True))[0][1]['x']
    START_NODE = list(req_g.nodes(data=True))[0][0]
    for n in list(req_g.nodes(data=True)):
        if n[1]['x'] < x:
            x = n[1]['x']
            START_NODE = n[0]
    return START_NODE

def remove_granular_connector_edges(inner_g_strongly_connected):
    """
    Removes granular connector edges from graph
    Args:
        inner_g_strongly_connected (NetworkX MultiDiGraph): strongly_connected street network graph
    Returns:
        inner_g_strongly_connected (NetworkX MultiDiGraph): strongly_connected street network graph with
        granular connector edges removed (contracted connector edges intact)
        GranularConnector_EdgeList (list): list of granular connector edges
    """
    inner_g_strongly_connected_copy = inner_g_strongly_connected.copy()
    GranularConnector_EdgeList = []
    for e in inner_g_strongly_connected.edges(data=True, keys=True):
        if e[3].get('granular_type') == 'connector':
            u = e[0]
            v = e[1]
            key = e[2]
            inner_g_strongly_connected_copy.remove_edge(u, v, key=key)
            GranularConnector_EdgeList += [[u, v]]
    print('\n{} Granular Connector Edges'.format(len(GranularConnector_EdgeList)))
    return inner_g_strongly_connected_copy, GranularConnector_EdgeList

def add_distance_keys_to_graph(graph):
    graph_copy =graph.copy()
    for e in graph.edges(data=True, keys = True):
        u = e[0]
        v = e[1]
        key = e[2]
        distance = graph[u][v][key]['length']
        graph_copy[u][v][key]['distance'] = distance
    return graph_copy
