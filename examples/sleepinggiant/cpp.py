import json
import pkg_resources

from postman_problems.graph import cpp


if __name__ == '__main__':

    # Creating config
    config = {
        "data": {
            "edgelist": pkg_resources.resource_filename('examples', 'sleepinggiant/edgelist_sleeping_giant.csv'),
            "nodelist": pkg_resources.resource_filename('examples', 'sleepinggiant/nodelist_sleeping_giant.csv'),
            "edge_attr_distance": "distance",
            "starting_node": "b_end_east"
        }
    }

    # get the CPP solution
    circuit = cpp(config)

    # print the solution
    for e in circuit:
        print(e)


