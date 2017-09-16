import sys
import pkg_resources
from unittest.mock import patch
from postman_problems.chinese_postman import main


# input params
EDGELIST_SEVEN_BRIDGES = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/edgelist_seven_bridges.csv')
EDGELIST_SLEEPING_GIANT = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')

# output params
OUT_SEVEN_BRIDGES_SVG = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph.svg')
OUT_SEVEN_BRIDGES_GIF = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph.gif')
OUT_SLEEPING_GIANT_SVG = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/cpp_graph.svg')


# TODO: add more parameterizations with visualizations
def test_chinese_postman_seven_bridges():
    testargs = ["chinese_postman", "--edgelist", EDGELIST_SEVEN_BRIDGES]
    with patch.object(sys, 'argv', testargs):
        main()


# TODO: add more parameterizations with visualizations
def test_chinese_postman_sleeping_giant():
    testargs = ["chinese_postman", "--edgelist", EDGELIST_SLEEPING_GIANT]
    with patch.object(sys, 'argv', testargs):
        main()
