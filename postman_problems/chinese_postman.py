import argparse
from postman_problems.graph import cpp


def get_args():
    """
    Returns:
        argparse.Namespace: parsed arguments from the user
    """
    parser = argparse.ArgumentParser(description='Arguments to the Chinese Postman Problem solver')

    parser.add_argument('--edgelist_filename',
                        required=True,
                        type=str,
                        help='Filename of edgelist.'
                             'Expected to be comma delimited text file readable with pandas.read_csv'
                             'The first two columns should be the "from" and "to" node names.'
                             'Additional columns can be provided for edge attributes.'
                             'The first row should be the edge attribute names.')
    parser.add_argument('--nodelist_filename',
                        required=False,
                        type=str,
                        default=None,
                        help='Filename of node attributes (optional).'
                             'Expected to be comma delimited text file readable with pandas.read_csv'
                             'The first column should be the node name.'
                             'Additional columns should be used to provide node attributes.'
                             'The first row should be the node attribute names.')
    parser.add_argument('--start_node',
                        required=False,
                        type=str,
                        default=None,
                        help='Node to start the CPP solution from (optional).'
                             'If not provided, a starting node will be selected at random.')
    parser.add_argument('--edge_weight',
                        required=False,
                        type=str,
                        default='distance',
                        help='Edge attribute used to specify the distance between nodes (optional).'
                             'Default is "distance".')

    return parser.parse_args()


if __name__ == '__main__':
    """
    Parse command line arguments and solve the CPP
    """

    # parse arguments
    args = get_args()

    # solve CPP
    cpp_solution = cpp(edgelist_filename=args.edgelist_filename,
                       start_node=args.start_node,
                       edge_weight=args.edge_weight)

    # print solution
    [print(edge) for edge in cpp_solution]



