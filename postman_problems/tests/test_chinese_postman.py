import sys
import os
import pytest
import tempfile
import shutil
import pkg_resources
from unittest.mock import patch
from postman_problems.chinese_postman import main
from pytest_console_scripts import script_runner


# input params
EDGELIST_SEVEN_BRIDGES = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/edgelist_seven_bridges.csv')
EDGELIST_SLEEPING_GIANT = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/edgelist_sleeping_giant.csv')
NODELIST_SLEEPING_GIANT = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/nodelist_sleeping_giant.csv')

# output params
OUT_SEVEN_BRIDGES_SVG = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph.svg')
OUT_SEVEN_BRIDGES_GIF = pkg_resources.resource_filename('postman_problems', 'examples/seven_bridges/output/cpp_graph.gif')
OUT_SLEEPING_GIANT_SVG = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/cpp_graph.svg')
OUT_SLEEPING_GIANT_GIF = pkg_resources.resource_filename('postman_problems', 'examples/sleeping_giant/output/cpp_graph.gif')


def test_chinese_postman_seven_bridges():
    """
    Test command line usage of chinese_postman
    Outputs are written to a temp directory, checked and then cleaned up.
    """

    tmpdir = tempfile.mkdtemp()
    saved_umask = os.umask(00)  # 0077

    testargs = ["chinese_postman",
                "--edgelist", EDGELIST_SEVEN_BRIDGES,
                "--viz_static",
                "--viz_animation",
                "--viz_static_filename", os.path.join(tmpdir, 'test_cpp_graph'),
                "--viz_animation_filename", os.path.join(tmpdir, 'test_cpp_graph.gif')
                ]
    with patch.object(sys, 'argv', testargs):
        main()

    assert os.path.isfile(os.path.join(tmpdir, 'test_cpp_graph.png'))
    assert os.path.isfile(os.path.join(tmpdir, 'test_cpp_graph.gif'))

    # clean up
    os.umask(saved_umask)
    shutil.rmtree(tmpdir)


def test_chinese_postman_sleeping_giant():
    testargs = ["chinese_postman",
                "--edgelist", EDGELIST_SLEEPING_GIANT,
                "--nodelist", NODELIST_SLEEPING_GIANT
                ]
    with patch.object(sys, 'argv', testargs):
        main()


def test_entry_point_example_chinese_postman_seven_bridges(script_runner):
    """
    Just testing that seven_bridges example runs with pre-parameterized config.
    Will overwrite output in the examples dir... that's OK.
    """
    ret = script_runner.run('chinese_postman_seven_bridges')
    assert ret.success
    assert os.path.isfile(OUT_SEVEN_BRIDGES_SVG)
    assert os.path.isfile(OUT_SEVEN_BRIDGES_GIF)


@pytest.mark.slow
@pytest.mark.main
def test_entry_point_example_chinese_postman_sleeping_giant(script_runner):
    """
    Just testing that Sleeping Giant example run with pre-parameterized config.
    Will overwrite output in the examples dir... that's OK.
    """
    ret = script_runner.run('chinese_postman_sleeping_giant')
    assert ret.success
    assert os.path.isfile(OUT_SLEEPING_GIANT_SVG)
    assert os.path.isfile(OUT_SLEEPING_GIANT_GIF)
