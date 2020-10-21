import itertools
import networkx as nx
import postman_problems.shortest_path_mod as spm
import numpy as np
import pandas as pd
from copy import deepcopy
from collections import defaultdict
from compassbearing import calculate_initial_compass_bearing
from osm2nx import haversine


def states_to_state_avenue_name(state_list):
    """
    Creates all possible candidate State Avenues in form of 'Georgia Avenue Southwest' matching OSM names
    Args:
        state_list (list[str]): list of states to calculate state avenue names for
    Returns:
        list of state avenue names w quadrant
    """
    state_avenue = ['{} Avenue'.format(state) for state in state_list]
    st_types = ['Ave', 'Avenue']

    # most OSM edges use the long form name, but some use the short form abbreviation.
    quadrant = ['Southeast', 'Southwest', 'Northeast', 'Northwest', 'SE', 'SW', 'NE', 'NW']
    state_avenue_quadrant = ['{} {} {}'.format(state, st, quad) for state in state_list for st in st_types for quad in quadrant]
    return state_avenue_quadrant


def subset_graph_by_edge_name(graph, keep_edge_names):
    """
    Given the the full graph of DC (all roads), return a graph with just the state avenue
    Args:
        graph (networkx graph): full graph w
        keep_edge_names (list): list of edge names to keep
    Returns:
        desired subset of graph where the edge attribute `name` is contained in `keep_edge_names`
    """

    # create graph with state avenues only
    graph = nx.to_undirected(graph.copy())
    g_sub = graph.copy()
    for e in graph.edges(data=True):
        if ('name' not in e[2]) or (e[2]['name'] not in keep_edge_names):
            g_sub.remove_edge(e[0], e[1])
    return g_sub


def keep_oneway_edges_only(graph):
    """
    Given a starter graph, remove all edges that are not explicitly marked as 'oneway'.  Also removes nodes that are not
    connected to one-way edges.
    Args:
        graph (networkx graph): base graph
    Returns:
        networkx graph without one-way edges or nodes
    """
    g1 = graph.copy()

    # remove edges that are not oneway
    for e in list(g1.edges(data=True)):
        if ('oneway' not in e[2]) or (e[2]['oneway'] != True):
            g1.remove_edge(e[0], e[1])

    # remove nodes that are not connected to oneway edges
    keepnodes = list(itertools.chain(*list(g1.edges())))
    for node in set(g1.nodes) - set(keepnodes):
        g1.remove_node(node)
    return g1


def create_connected_components(graph):
    """
    Breaks a graph apart into non overlapping components (subgraphs). Nodes with 3 or more edges are removed which
    effectively splits the graph into sub-components.  This each component will resembles a single road constructed
    of multiple edges strung out in a line, but no intersections.
    Args:
        graph (networkx graph):
    Returns:
        list of connected components where each component is a networkx graph
    """

    # remove nodes with degree > 2
    graph_d2 = graph.copy()
    remove_nodes = []
    for node in graph.nodes():
        if graph_d2.degree(node) > 2:
            remove_nodes.append(node)
        graph_d2.remove_nodes_from(remove_nodes)

    # get connected components from graph with
    comps = [graph_d2.subgraph(c).copy() for c in nx.strongly_connected_components(graph_d2)]
    comps = [non_empty_comp for non_empty_comp in comps if len(non_empty_comp.edges()) > 0]
    return comps


def is_graph_line_or_circle(graph):
    """
    Determine if a graph is a line or a circle.  Lines have exactly two nodes with degree 1.  Circles have all degree 2 nodes.
    Args:
        graph (networkx graph):
    Returns:
        string: 'line' or 'circle'
    """
    degree1_nodes = [n[0] for n in graph.degree() if n[1] == 1]

    if len(degree1_nodes) == 2:
        edge_type = 'line'
    elif len(degree1_nodes) == 0:
        edge_type = 'circle'
    else:
        raise ValueError('Number of nodes with degree-1 is not equal to 0 or 2... it should be.')

    if max([n[1] for n in graph.degree()]) > 2:
        raise ValueError('One or more nodes with degree < 2 detected.  All nodes must have degree 1 or 2.')

    return edge_type


def _sort_nodes(graph):
    """
    NetworkX does not preserve any node order for edges in MultiDiGraphs.  Given a graph (component) where all nodes are
    of degree 1 or 2, this calculates the sequence of nodes from one node to the next.  If the component has any nodes
    with degree 1, it must have exactly two nodes of degree 1 by this constraint (long road, strung out like a line).
    One of the 1-degree nodes are chosen as the start-node. If all nodes have degree 2, we have a loop and the start/end
    node is chosen arbitrarily.
    Args:
        graph (networkx graph):
    Returns:
        list of node ids that constitute a direct path (tour) through each node.
    """

    edge_type = is_graph_line_or_circle(graph)
    degree1_nodes = [n[0] for n in graph.degree() if n[1] == 1]

    if edge_type == 'line':
        start_node, end_node = degree1_nodes
        nodes = spm.dijkstra_path(graph, start_node, end_node)
    elif edge_type == 'circle':
        nodes = [n[0] for n in list(nx.eulerian_circuit(graph))]
    else:
        raise RuntimeError('Unrecognized edge_type')

    assert len(nodes) == len(graph.nodes())

    return nodes


# TODO: handle the circular 0 - 360 degree comparison issue
def _calculate_bearings(graph, nodes):
    """
    Calculate the compass bearings for each sequential node paid in `nodes`.  Lat/lon coordinates are expected to be
    node attributes in `graph` named 'y' and 'x'.
    Args:
        graph (networkx graph):  containing lat/lon coordinates of each node in `nodes`
        nodes (list): list of nodes in sequential order that bearings will be calculated
    Returns:
        list[float] of the bearings between each node pair
    """

    # bearings list
    bearings = []
    edge_type = is_graph_line_or_circle(graph)

    node_pairs = list(zip(nodes[:-1], nodes[1:]))
    if edge_type == 'circle':
        node_pairs = [(nodes[-1], nodes[0])] + node_pairs + [(nodes[-1], nodes[0])]

    for pair in node_pairs:
        comp_bearing = calculate_initial_compass_bearing(
            (graph.nodes[pair[0]]['x'], graph.nodes[pair[0]]['y']),
            (graph.nodes[pair[1]]['x'], graph.nodes[pair[1]]['y'])
        )
        bearings.append((pair[0], pair[1], comp_bearing))

    return bearings


def _diff_bearings(bearings, bearing_thresh=40):
    """
    Identify kinked nodes (nodes that change direction of an edge) by diffing
    Args:
        bearings (list(tuple)): containing (start_node, end_node, bearing)
        bearing_thresh (int): threshold for identifying kinked nodes (range 0, 360)
    Returns:
        list[str] of kinked nodes
    """

    kinked_nodes = []

    # diff bearings
    nodes = [b[0] for b in bearings]
    bearings_comp = [b[2] for b in bearings]
    bearing_diff = [y - x for x, y in zip(bearings_comp, bearings_comp[1:])]
    node2bearing_diff = list(zip(nodes[1:-1], bearing_diff))

    # id nodes to remove
    for n in node2bearing_diff:
        # controlling for differences on either side of 360
        if min(abs(n[1]), abs(n[1] - 360)) > bearing_thresh:
            kinked_nodes.append(n[0])

    return kinked_nodes


def identify_kinked_nodes(comp, bearing_thresh=40):
    """
    Identify kinked nodes in a connected component.  Used to split one-way roads that connect at one or both ends.
    Removing these kinked nodes (and splitting these edges) is an important step in identifying parallel roads of the
    same name (mostly due to divided highways or one-ways).
    Args:
        comp (networkx graph): connected component to calculate kinked nodes from.  Nodes should be of degree 1 or 2.
        bearing_thresh (int): threshold for identifying kinked nodes (range 0, 360)
    Returns:
        list[str] of kinked nodes
    """

    # sort nodes in sequential order, a tour
    sorted_nodes = _sort_nodes(comp)

    # calculate bearings for each node pair
    bearings = _calculate_bearings(comp, sorted_nodes)

    # calculate node pairs where
    kinked_nodes = _diff_bearings(bearings, bearing_thresh)

    return kinked_nodes


def create_unkinked_connected_components(comps, bearing_thresh):
    """
    Create a list of unkinked connected components to compare.
    Args:
        comps (list[networkx graph]): list of components to unkink.  Each component should be a graph where all nodes are degree 1 or 2.
        bearing_thresh (int): threshold for identifying kinked nodes (range 0, 360)
    Returns:
        list of unkinked components (likely more provided in `comps`) with some additional metadata (graph level attrs)
    """

    comps_unkinked = []

    comps2unkink = deepcopy(comps)
    # create new connected components without kinked nodes
    for comp in comps2unkink:
        kinked_nodes = identify_kinked_nodes(comp, bearing_thresh)
        comp.remove_nodes_from(kinked_nodes, )

        comps_broken = [comp.subgraph(c).copy() for c in nx.strongly_connected_components(comp)]
        comps_unkinked += [non_empty_comp for non_empty_comp in comps_broken if len(non_empty_comp.edges()) > 0]

    # Add graph level attributes
    for i, comp in enumerate(comps_unkinked):
        comp_edge = list(comp.edges(data=True))[0]  # just take first edge

        # adding road name.  Removing the last
        comp.graph['name'] = comp_edge[2]['name'] if 'name' in comp_edge[2] else 'unnamed_road_{}'.format(str(i))
        comp.graph['id'] = i

    return comps_unkinked


def nodewise_distance_connected_components(comps):
    """
    Calculate minimum haversine distance between points in each connected component which share the same graph name
    (road/edge name in our case).  Used to detect redundant parallel edges which will be removed for the 50 states problem.
    Args:
        comps list[networkx graph]: list of components to search for parallel edges
    Returns:
        dictionary: state_name : comp_id : cand_id: list of distances measuring shortest distance for each node in comp_id
                                                    to closest node in cand_id.
    """
    matches = defaultdict(dict)

    for i, comp in enumerate(comps):

        matches[comp.graph['name']][comp.graph['id']] = dict()

        # candidate components are those with the same street name (possible contenders for parallel edges)
        candidate_comps = [cand for cand in comps if
                           comp.graph['name'] == cand.graph['name'] and comp.graph['id'] != cand.graph['id']]

        # check distance from every node in comp to closest corresponding node in each cand.
        for cand in candidate_comps:
            cand_pt_closest_cands = []

            for n1 in comp.nodes():
                pt_closest_cands = []

                for n2 in cand.nodes():
                    pt_closest_cands.append(
                        haversine(comp.nodes[n1]['x'], comp.nodes[n1]['y'], cand.nodes[n2]['x'],
                                  cand.nodes[n2]['y'])
                    )
                # calculate distance to the closest node in candidate component to n1 (from starting component)
                cand_pt_closest_cands.append(min(pt_closest_cands))

            # add minimum distance
            matches[comp.graph['name']][comp.graph['id']][cand.graph['id']] = cand_pt_closest_cands

    return matches


def calculate_component_overlap(matches, thresh_distance):
    """
    Calculate how much each connected component is made redundant (percent of nodes that have a neighbor within some
    threshold distance) by each of its candidates.
    Args:
        matches (dict): output from `nodewise_distance_connected_components` with nodewise distances between components.
        thresh_distance (int): threshold in meters for saying nodes are "close enough" to be redundant.
    Returns:
        dict where `pct_nodes_dupe` indicates how many nodes in `comp` are redundant in `cand`
    """

    comp_overlap = []
    for road in matches:
        for comp in matches[road]:
            for cand in matches[road][comp]:
                n_dist = matches[road][comp][cand]
                pct_nodes_dupe = sum(np.array(n_dist) < thresh_distance) / len(n_dist)
                comp_overlap.append({'road': road, 'comp': comp, 'cand': cand, 'pct_nodes_dupe': pct_nodes_dupe})

    return comp_overlap


def calculate_redundant_components(comp_overlap, thresh_pct=0.85):
    """
    Calculates which components are redundant using the overlap data structure created from `calculate_component_overlap`.
    The algorithm employed is a bit of heuristic that essentially iteratively removes components that are mostly
    (subject to `thresh_pct`) covered by another component.
    Args:
        comp_overlap (list[dict]): created from `calculate_component_overlap`.
        thresh_pct (float): percentage of nodes in comp that must be within thresh_distance of the nearest node in a
                            candidate component
    Returns:
        dictionary for remove and keep components respectively.  Keys are graph names (state avenues).  Values are
        a set of component_ids.
    """

    keep_comps = {}
    remove_comps = {}

    for road in set([x['road'] for x in comp_overlap]):
        df = pd.DataFrame(comp_overlap)
        df = df[df['road'] == road]
        df.sort_values('pct_nodes_dupe', inplace=True, ascending=False)

        road_removed_comps = []
        for row in df.iterrows():
            if row[1]['pct_nodes_dupe'] > thresh_pct:
                if (row[1]['cand'] in road_removed_comps) or (row[1]['comp'] in road_removed_comps):
                    continue
                df.drop(row[0], inplace=True)
                road_removed_comps.append(row[1]['comp'])

        keep_comps[road] = set(df['comp']) - set(road_removed_comps)
        remove_comps[road] = set(road_removed_comps)

    return remove_comps, keep_comps


def create_deduped_state_road_graph(graph_st, comps_dict, remove_comp_ids):
    """
    Creates a single graph with all state roads deduped of parallel one way roads with the same name
    Args:
        graph_st (networkx graph): with all state roads
        comps_dict (dict): mapping from graph id to component (graph)
        remove_comp_ids (list[int]): list of components (by id) to remove from `graph_st`.  These are the parallel one
         way edges and nodes left without any incident edges.
    Returns:
        NetworkX graph all state roads deduped for parallel one way roads
    """

    graph_st_deduped = graph_st.copy()

    # actually remove dupe one-way edges from g_st
    comps2remove = list(itertools.chain(*remove_comp_ids.values()))
    for cid in comps2remove:
        comp = comps_dict[cid]
        graph_st_deduped.remove_nodes_from(comp.nodes(), )

    # remove nodes w no edges
    remove_island_nodes = []
    for node in graph_st_deduped.nodes():
        if graph_st_deduped.degree(node) == 0:
            remove_island_nodes.append(node)
    graph_st_deduped.remove_nodes_from(remove_island_nodes)

    return graph_st_deduped


# TODO: implement smarter handling of degree 2 nodes that form a loop w only one node w degree > 2.
#JC if statement to handle components with 1 or 0 nodes greater than degree 2
def contract_edges(graph, edge_weight='weight'):
    """
    Given a graph, contract edges into a list of contracted edges.  Nodes with degree 2 are collapsed into an edge
    stretching from a dead-end node (degree 1) or intersection (degree >= 3) to another like node.
    Args:
        graph (networkx graph):
        edge_weight (str): edge weight attribute to us for shortest path calculations
    Returns:
        List of tuples representing contracted edges
    """

    if len([n for n in graph.nodes() if graph.degree(n) > 2]) > 1:
        keep_nodes = [n for n in graph.nodes() if graph.degree(n) != 2]
        contracted_edges = []

        for n in keep_nodes:
            for nn in nx.neighbors(graph, n):

                nn_hood = set(nx.neighbors(graph, nn)) - {n}
                path = [n, nn]

                if len(nn_hood) == 1:
                    while len(nn_hood) == 1:
                        nnn = list(nn_hood)[0]
                        nn_hood = set(nx.neighbors(graph, nnn)) - {path[-1]}
                        path += [nnn]

                full_edges = list(zip(path[:-1], path[1:]))  # granular edges between keep_nodes
                spl = sum([graph[e[0]][e[1]][0][edge_weight] for e in full_edges])  # distance

                # only keep if path is unique.  Parallel/Multi edges allowed, but not those that are completely redundant.
                if (not contracted_edges) | ([set(path)] not in [[set(p[3])] for p in contracted_edges]):
                    contracted_edges.append(tuple(sorted([n, path[-1]])) + (spl,) + (path,))
    else:
        contracted_edges = []
        for e in graph.edges(data=True):
            edge = (e[0], e[1], e[2][edge_weight], [e[0], e[1]])
            contracted_edges += [edge]

    return contracted_edges


def create_contracted_edge_graph(graph, edge_weight):
    """
    Creates a fresh graph with contracted edges only.
    Args:
        graph (networkx graph): base graph
        edge_weight (str): edge attribute for weight used in `contract_edges`
    Returns:
        networkx graph with contracted edges and nodes only
    """

    graph_contracted = nx.MultiDiGraph()
    for i, comp in enumerate([graph.subgraph(c).copy() for c in nx.strongly_connected_components(graph)]):
        for cc in contract_edges(comp, edge_weight):
            start_node, end_node, distance, path = cc

            if 'name' in graph[path[0]][path[1]]:
                street_name = graph[path[0]][path[1]]['name']
            else:
                street_name = 'unlabeled'

            contracted_edge = {
                'start_node': start_node,
                'end_node': end_node,
                'distance': distance,
                'start_edge_name': street_name,
                'comp': i,
                'required': 1,
                'path': path
            }

            graph_contracted.add_edge(start_node, end_node, **contracted_edge)

            graph_contracted.nodes[start_node]['comp'] = i
            graph_contracted.nodes[end_node]['comp'] = i
            graph_contracted.nodes[start_node]['y'] = graph.nodes[start_node]['y']
            graph_contracted.nodes[start_node]['x'] = graph.nodes[start_node]['x']
            graph_contracted.nodes[end_node]['y'] = graph.nodes[end_node]['y']
            graph_contracted.nodes[end_node]['x'] = graph.nodes[end_node]['x']

    return graph_contracted

#JC replacement for contract_edges in strongly_connected_comp_splitter
def connected_comp_edge_handler(graph, edge_weight='weight'):
    """
    Modified version of contract_edges used to handle edges in strongly_connected_comp_splitter. Modified by JC.
    Args:
        graph (NetworkX MultiDiGraph): strongly connected component graph
        edge_weight (str): edge attribute to use as weight
    Returns:
        list of tuples: [(edge node 1, edge node 2, edge attr dict)]
    """
    packaged_edges = []
    for e in graph.edges(data=True):
        if 'name' in e[2]:
            street_name = e[2]['name']
        elif 'junction' in e[2]:
            street_name = 'junction_' + e[2]['junction']
        else:
            street_name = 'unlabeled'
        attr = {
                'start_node': e[0],
                'end_node': e[1],
                'distance': e[2][edge_weight],
                'path': [e[0], e[1]],
                'turn_length' : e[2]['turn_length'],
                'length': e[2][edge_weight],
                'name': street_name,
                'required': 1,
                }

        edge = (e[0], e[1], attr)
        packaged_edges += [edge]
    return packaged_edges

#JC break graph into strongly connected components with nodes and edges designated by their respective components.
def strongly_connected_comp_splitter(graph, edge_weight):
    """
    Written by JC
    Breaks graph into strongly connected components. Removes components with no edges.
    Adds all edges and nodes contained by strongly connected components to a new graph. Labels nodes and edges by a component ID.
    Since this function substitutes for a function that contracted edges in addition to splitting components,
    this version continues to add a 'path' attribute that is used in subsequent functions.
    Args:
        graph (Networkx DiGraph): graph of required edges
        edge_weight (str): edge attribute to designate as a weight
    Returns:
        MultiDiGraph of strongly connected components with edge attributes catered for subsequent functions
    """
    graph_split = nx.MultiDiGraph()
    removed_comps = []
    comp_list = []
    print('\nInitial Strongly Connected Component Breakdown')
    for i, comp in enumerate([graph.subgraph(c).copy() for c in nx.strongly_connected_components(graph)]):
        print('Comp: {}'.format(i))
        print('\tEdges: {}'.format(len(comp.edges())))
        print('\tNodes: {}'.format(len(comp.nodes())))
        #for n in comp.nodes():
            #print(comp.degree(n))
        #exclude components with only 1 node
        if len(comp.nodes()) > 1:
            comp_list+=[i]
            for cc in connected_comp_edge_handler(comp, edge_weight):
                start_node, end_node, attr = cc

                attr['comp'] = i
                graph_split.add_edge(start_node, end_node, **attr)

                graph_split.nodes[start_node]['comp'] = i
                graph_split.nodes[end_node]['comp'] = i
                graph_split.nodes[start_node]['y'] = graph.nodes[start_node]['y']
                graph_split.nodes[start_node]['x'] = graph.nodes[start_node]['x']
                graph_split.nodes[end_node]['y'] = graph.nodes[end_node]['y']
                graph_split.nodes[end_node]['x'] = graph.nodes[end_node]['x']
        else:
            removed_comps+=[i]
    for comp in removed_comps:
        print('Comp {} removed'.format(comp))
    comp_corrector_dic = {}
    for i in range(0, len(comp_list)):
        comp_corrector_dic[comp_list[i]] = i
    graph_split_copy = graph_split.copy()
    for edge in graph_split.edges(data=True):
        #rename comp
        graph_split_copy[edge[0]][edge[1]][0]['comp'] = comp_corrector_dic[edge[2]['comp']]
        #remove parallel edges
        if 1 in graph_split_copy[edge[0]][edge[1]]:
            graph_split_copy.remove_edge(edge[0], edge[1], key = 1)
    print('Comp numbers reordered')
    print('Parallel edges removed')
    graph_split = graph_split_copy
    return graph_split


#JC modified for directed graphs to include both orientations of pairs 
def shortest_paths_between_components(graph):
    """
    Calculate haversine distances for all possible combinations of cross-component node-pairs
    Args:
        graph (networkx graph): with contracted edges and nodes only.  Created from `create_contracted_edge_graph`.
    Returns:
        Dataframe with haversine distances all possible combinations of cross-component node-pairs
    """

    # calculate nodes incident to contracted edges
    contracted_nodes = []
    for e in graph.edges(data=True):
        if ('required' in e[2]) and (e[2]['required'] == 1):
            contracted_nodes += [e[0], e[1]]
    contracted_nodes = set(contracted_nodes)

    # Find closest connected components to join
    dfsp_list = []
    same_comp = []
    diff_comp = []
    for n1 in contracted_nodes:
        for n2 in set(contracted_nodes) - {n1}:
            if graph.nodes[n1]['comp'] == graph.nodes[n2]['comp']:
                same_comp+=[1]
                continue
            diff_comp+=[1]
            
            haversine_distance = haversine(graph.nodes[n1]['x'], graph.nodes[n1]['y'], 
                    graph.nodes[n2]['x'], graph.nodes[n2]['y'])
            start_comp = graph.nodes[n1]['comp']
            end_comp = graph.nodes[n2]['comp']

            dfsp_list.append({
                'start_node': n1,
                'end_node': n2,
                'haversine_distance': haversine_distance, 
                'start_comp': start_comp,
                'end_comp': end_comp
            })
            dfsp_list.append({
                'start_node': n2,
                'end_node': n1,
                'haversine_distance': haversine_distance, 
                'start_comp': end_comp,
                'end_comp': start_comp
            })

    dfsp = pd.DataFrame(dfsp_list)
    dfsp.sort_values('haversine_distance', inplace=True)

    return dfsp


#JC modified to generate reverse paths in addition to forward paths
def find_minimum_weight_edges_to_connect_components(dfsp, graph, edge_weight='distance', top=10):
    """
    Given a dataframe of haversine distances between many pairs of nodes, calculate the min weight way to connect all
    the components in `graph`.  At each iteration, the true shortest path (dijkstra_path_length) is calculated for the
     top `top` closest node pairs using haversine distance.  This heuristic improves efficiency at the cost of
     potentially not finding the true min weight connectors.  If this is a concern, increase `top`.
    Args:
        dfsp (dataframe): calculated with `shortest_paths_between_components` with haversine distance between all node
                          candidate node pairs
        graph (networkx graph): used for the true shortest path calculation
        edge_weight (str): edge attribute used shortest path calculation in `graph`
        top (int): number of pairs for which shortest path calculation is performed at each iteration
    Returns:
        list[tuple3] containing just the connectors needed to connect all the components in `graph`.
    """

    # find shortest edges to add to make one big connected component
    dfsp = dfsp.copy()
    new_required_edges = []
    while sum(dfsp.index[dfsp['start_comp'] != dfsp['end_comp']]) > 0:

        # calculate path distance for top 10 shortest
        dfsp['path_distance'] = None
        dfsp['path'] = dfsp['path2'] = [[]] * len(dfsp)

        for i in dfsp.index[dfsp['start_comp'] != dfsp['end_comp']][0:top]:
            if dfsp.loc[i]['path_distance'] is None:
                dfsp.loc[i, 'path_distance'] = spm.dijkstra_path_length(graph,
                                                                       dfsp.loc[i, 'start_node'],
                                                                       dfsp.loc[i, 'end_node'],
                                                                       edge_weight)
                dfsp.at[i, 'path'] = spm.dijkstra_path(graph,
                                                      dfsp.loc[i, 'start_node'],
                                                      dfsp.loc[i, 'end_node'],
                                                      edge_weight)
                dfsp.at[i, 'length'] = nx.dijkstra_path_length(graph,
                                                      dfsp.loc[i, 'start_node'],
                                                      dfsp.loc[i, 'end_node'],
                                                      'length')

        dfsp.sort_values('path_distance', inplace=True)

        # The first index where start and end comps are different is the index containing the shortest connecting path between start comp and end comp
        first_index = dfsp.index[dfsp['start_comp'] != dfsp['end_comp']][0]
        start_comp = dfsp.loc[first_index]['start_comp']
        end_comp = dfsp.loc[first_index]['end_comp']
        start_node = dfsp.loc[first_index]['start_node']
        end_node = dfsp.loc[first_index]['end_node']
        path_distance = dfsp.loc[first_index]['path_distance']
        path = dfsp.loc[first_index]['path']
        length = dfsp.loc[first_index]['length']
        
        dfsp_rev_pair = dfsp[dfsp['start_comp'] == end_comp] 
        dfsp_rev_pair = dfsp_rev_pair[dfsp_rev_pair['end_comp'] == start_comp]
        for i in dfsp_rev_pair.index[0:top]: 
             if dfsp_rev_pair.loc[i]['path_distance'] is None:
                dfsp_rev_pair.loc[i, 'path_distance'] = spm.dijkstra_path_length(graph,
                                                                       dfsp_rev_pair.loc[i, 'start_node'],
                                                                       dfsp_rev_pair.loc[i, 'end_node'],
                                                                       edge_weight)
                dfsp_rev_pair.at[i, 'path'] = spm.dijkstra_path(graph,
                                                      dfsp_rev_pair.loc[i, 'start_node'],
                                                      dfsp_rev_pair.loc[i, 'end_node'],
                                                      edge_weight)
                dfsp_rev_pair.at[i, 'length'] = nx.dijkstra_path_length(graph,
                                                      dfsp.loc[i, 'start_node'],
                                                      dfsp.loc[i, 'end_node'],
                                                      'length')

        dfsp_rev_pair.sort_values('path_distance', inplace=True)

        first_index_rev = dfsp_rev_pair.index[0]
        start_node_rev = dfsp_rev_pair.loc[first_index_rev]['start_node']
        end_node_rev = dfsp_rev_pair.loc[first_index_rev]['end_node']
        path_distance_rev = dfsp_rev_pair.loc[first_index_rev]['path_distance']
        path_rev = dfsp_rev_pair.loc[first_index_rev]['path']
        length_rev = dfsp_rev_pair.loc[first_index_rev]['length']
           
        dfsp.loc[dfsp['end_comp'] == end_comp, 'end_comp'] = start_comp
        dfsp.loc[dfsp['start_comp'] == end_comp, 'start_comp'] = start_comp
        dfsp.sort_values('haversine_distance', inplace=True)
        new_required_edges.append((start_node, end_node, {'distance': path_distance, 'path': path, 'length': length, 'start_comp': start_comp, 'end_comp': end_comp}))
        new_required_edges.append((start_node_rev, end_node_rev, {'distance': path_distance_rev, 'length': length_rev, 'path': path_rev, 'start_comp': end_comp, 'end_comp': start_comp}))

    return new_required_edges


#JC modified for directed implementation with turning conditions.
# does not add granular connector edges to edgelist, 
# adds 'length' to attribute dictionary in addition to 'distance'. 'distance' is used as a weighting and is a function of
# turn weight in addition to edge length. 'length' is the unaltered edge length that will be used for route distance statistics.
def create_rpp_edgelist(g_strongly_connected, graph_full, edge_weight='distance', max_distance=1600):
    """
    Create the edgelist for the RPP algorithm.  This includes:
     - Required state edges (deduped)
     - Required non-state roads that connect state roads into one connected component with minimum additional distance
     - Optional roads that connect the nodes of the contracted state edges (these distances are calculated here using
       first haversine distance to filter the candidate set down using `max_distance` as a threshold, then calculating
       the true shortest path distance)
    Args:
        g_strongly_connected (networkx MultiDiGraph): of strongly connected roads
        graph_full (networkx Graph): full graph with all granular edges
        edge_weight (str): edge attribute for distance in `g_strongly_connected` and `graph_full`
        max_distance (int): max haversine distance used to add candidate optional edges for.
    Returns:
        Dataframe of edgelist described above.
    """

    dfrpp_list = []
    for e in g_strongly_connected.edges(data=True):
        if 'granular' not in e[2]:
            dfrpp_list.append({
                'start_node': e[0],
                'end_node': e[1],
                'distance_haversine': e[2]['distance'],
                'required': 1,
                'distance': e[2]['distance'],
                'path': e[2]['path'],
                'length': e[2]['length']
            })

    for n1, n2 in [comb for comb in itertools.combinations(g_strongly_connected.nodes(), 2)]:
        if n1 == n2:
            continue

        if not g_strongly_connected.has_edge(n1, n2):
            distance_haversine = haversine(g_strongly_connected.nodes[n1]['x'], g_strongly_connected.nodes[n1]['y'],
                                           g_strongly_connected.nodes[n2]['x'], g_strongly_connected.nodes[n2]['y'])

            # only add optional edges whose haversine distance is less than `max_distance`
            if distance_haversine > max_distance:
                continue

            dfrpp_list.append({
                'start_node': n1,
                'end_node': n2,
                'distance_haversine': distance_haversine,
                'required': 0,
                'distance': spm.dijkstra_path_length(graph_full, n1, n2, edge_weight),
                'path': spm.dijkstra_path(graph_full, n1, n2, edge_weight),
                'length': nx.dijkstra_path_length(graph_full, n1, n2, 'length')
            })

    # create dataframe
    dfrpp = pd.DataFrame(dfrpp_list)

    # create order
    dfrpp = dfrpp[['start_node', 'end_node', 'distance_haversine', 'distance', 'required', 'path', 'length']]

    return dfrpp
