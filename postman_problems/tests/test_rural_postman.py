import os
import sys
import pkg_resources
import pytest
from unittest.mock import patch
from pytest_console_scripts import script_runner
from postman_problems.postman_rural import rural_postman


# input params
EDGELIST_SLEEPING_GIANT = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
NODELIST_SLEEPING_GIANT = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/nodelist_sleeping_giant.csv')

# output params
OUT_SLEEPING_GIANT_SVG = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/rpp_graph.svg')
OUT_STAR_SVG = pkg_resources.resource_filename('postman_problems', 'examples/star/output/rpp_graph.svg')


@pytest.mark.slow
@pytest.mark.main
def test_entry_point_example_rural_postman_problem_sleeping_giant(script_runner):
    """
    Just testing that Sleeping Giant example runs with pre-parameterized config.
    Will overwrite output in the examples dir... that's OK.
    """
    ret = script_runner.run('rural_postman_sleeping_giant')
    assert ret.success
    assert os.path.isfile(OUT_SLEEPING_GIANT_SVG)


def test_entry_point_example_rural_postman_problem_star(script_runner):
    """
    Just testing that star example runs with pre-parameterized config.
    Will overwrite output in the examples dir... that's OK.
    """
    ret = script_runner.run('rural_postman_star')
    assert ret.success
    assert os.path.isfile(OUT_STAR_SVG)


def test_rural_postman_sleeping_giant():
    testargs = ["rural_postman",
                "--edgelist", EDGELIST_SLEEPING_GIANT,
                "--nodelist", NODELIST_SLEEPING_GIANT
                ]
    with patch.object(sys, 'argv', testargs):
        rural_postman()
