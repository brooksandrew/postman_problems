"""
Description:
    This example solves the CPP on the network derived from the Sleeping Giant State Park trail map

Usage:
    The simplest way to run this example is at the command line with the code below.  To experiment within an
    interactive python environment using an interpreter (ex, Jupyter notebook), remove the `if __name__ == '__main__':`
    line, and you should be good to go.
        ```
        python examples/sleepinggiant/cpp.py
        ````

    To run from the command line with different parameters, for example starting from a different node, try:
        ```
        python postman_problems/chinese_postman.py \
        --edgelist_filename 'examples/sleepinggiant/edgelist_sleeping_giant.csv' \
        --start_node 'rs_end_south'
        ```
"""

import pkg_resources
from postman_problems.graph import cpp
from postman_problems.viz import make_circuit_graphviz


if __name__ == '__main__':

    # params / data
    EDGELIST = pkg_resources.resource_filename('postman_problems', 'examples/sleepinggiant/edgelist_sleeping_giant.csv')
    NODELIST = pkg_resources.resource_filename('postman_problems', 'examples/leepinggiant/nodelist_sleeping_giant.csv')
    EDGE_WEIGHT = "distance"
    START_NODE = "b_end_east"

    # get the CPP solution
    circuit = cpp(EDGELIST, NODELIST, START_NODE, EDGE_WEIGHT)

    # print the solution
    for e in circuit:
        print(e)

    # visualize solution
        make_circuit_graphviz(circuit, ),


