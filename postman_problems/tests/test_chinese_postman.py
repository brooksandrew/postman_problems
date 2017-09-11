import math
import pkg_resources
from postman_problems.chinese_postman import cpp

# PARAMETERS / DATA

EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
START_NODE = 'b_end_east'

# TESTS


def test_sleeping_giant_cpp_solution():
    cpp_solution = cpp(edgelist_filename=EDGELIST, start_node=START_NODE)

    # make number of edges in solution is correct
    assert len(cpp_solution) == 154

    # make sure our total mileage is correct
    cpp_solution_distance = sum([edge[2]['distance'] for edge in cpp_solution])
    assert math.isclose(cpp_solution_distance, 33.59)

    # make sure our circuit begins and ends at the same place
    assert cpp_solution[0][0] == cpp_solution[-1][1] == START_NODE
