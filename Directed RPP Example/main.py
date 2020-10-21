#	File Created: 10/15/2020
#	Author: Jack Connor <jconnor@baaqmd.gov>

"""
Main file for running directed rpp with turning conditions.
Args:
    Polygon file identifier through command line input.
Returns:
    Status print statements and visualization plots.
    Routes in .csv and .gpx input.
"""

from postman_problems.solver import rpp
from postman_problems.stats import calculate_postman_solution_stats
from postman_problems.initialize_rpp import InnerAndOuterToEdgeListFile
import main_lib as ml

print('Enter Polygon File Identifier')
file_identifier = input()

turn_weight_coefficient = 10
input_file_directory = 'C:\\Users\jconnor\OneDrive - Bay Area Air Quality Management District\Documents\Projects\Maps\Route Testing\\'
print_directory = 'F:\python\ox\\route_results\\'
print_file = file_identifier + '_directed'


InnerFileName = file_identifier + ' Inner Polygon.csv'
OuterFileName = file_identifier + ' Outer Polygon.csv'


START_NODE, req_comp_g, complete_g, elfn, GranularConnector_EdgeList = InnerAndOuterToEdgeListFile(directory=input_file_directory, InnerFileName=InnerFileName, OuterFileName=OuterFileName, turn_weight_coefficient=turn_weight_coefficient)

circuit_rpp = rpp(elfn, complete_g, start_node = START_NODE, turn_weight_coefficient=turn_weight_coefficient)
circuit_rpp = ml.circuit_path_string_to_int(circuit_rpp)

req_and_opt_graph = ml.create_req_and_opt_graph(req_comp_g, complete_g, circuit_rpp, GranularConnector_EdgeList)

grppviz = ml.create_number_of_passes_graph(circuit_rpp, complete_g)

route_statistics = calculate_postman_solution_stats(circuit_rpp, edge_weight_name='length')

rppdf = ml.circuit_parser(circuit_rpp, complete_g, print_file, print_directory)

ml.gpx_writer(rppdf, print_file, print_directory)

ml.plot_req_and_opt_graph(req_and_opt_graph)

ml.plot_number_of_passes_graph(grppviz)
