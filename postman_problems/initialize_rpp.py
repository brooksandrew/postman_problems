#	File Created: 10/15/2020
#	Author: Jack Connor <jconnor@baaqmd.gov>

from postman_problems.tests.utils import create_mock_csv_from_dataframe
from graph import create_rpp_edgelist
import initialize_lib as il

def InnerAndOuterToEdgeListFile(directory = 'C:\\Users\jconnor\OneDrive - Bay Area Air Quality Management District\Documents\Projects\Maps\Route Testing\\',
        InnerFileName = 'Haight Inner Polygon.csv',
        OuterFileName = 'Haight Outer Polygon.csv', turn_weight_coefficient=1):

    inner_g, outer_g = il.create_inner_and_outer_graph(directory, InnerFileName, OuterFileName)

    inner_g = il.create_turn_weight_edge_attr(inner_g, normalization_coefficient=turn_weight_coefficient)
    outer_g = il.create_turn_weight_edge_attr(outer_g, normalization_coefficient=turn_weight_coefficient)

    inner_g = il.determine_and_remove_extraneous_reverse_edges(inner_g)

    il.simple_network_plotter(inner_g)

    inner_g_strongly_connected = il.strong_connector(inner_g, outer_g)

    il.strongly_connected_graph_plotter(inner_g_strongly_connected)

    START_NODE = il.pick_western_most_start_node(inner_g_strongly_connected)

    inner_g_strongly_connected, GranularConnector_EdgeList = il.remove_granular_connector_edges(inner_g_strongly_connected)    

    outer_g = il.add_distance_keys_to_graph(outer_g)

    dfrpp = create_rpp_edgelist(g_strongly_connected = inner_g_strongly_connected, graph_full = outer_g, edge_weight = il.turn_weight_function_distance, max_distance = 3200)

    elfn = create_mock_csv_from_dataframe(dfrpp)

    req_comp_g = inner_g_strongly_connected.copy()

    complete_g = outer_g.copy()

    return START_NODE, req_comp_g, complete_g, elfn, dfrpp, GranularConnector_EdgeList
