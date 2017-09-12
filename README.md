[![Build Status](https://travis-ci.org/brooksandrew/postman_problems.svg?branch=master)](https://travis-ci.org/brooksandrew/postman_problems)

[![Coverage Status](https://coveralls.io/repos/github/brooksandrew/postman_problems/badge.svg?branch=master)](https://coveralls.io/github/brooksandrew/postman_problems?branch=master)


## Postman Problems:

[Contents](#Contents)  
[Install](#Install)  
[Usage](#Usage)  
[Examples](#Examples)  
[Developers](#Developers)

## Contents

This package contains implementations to solve the suite of [Postman Problems] from graph theory.


Currently this is a suite of one: The Chinese Postman Problem, the most straightforward of the Postman Problems.  
The Rural Postman Problem will be added next.

## Install

Install the `postman_problems` package:

1. Clone the repo.  For now, just grab the master branch from GitHub.  When I release to PyPI, I'll make proper 0.1 release.
```
git clone https://github.com/brooksandrew/postman_problems.git
cd postman_problems
```

2. Install with pip.  
```
pip install .
```


## Usage

### 1. CLI

The easiest way to start is with the command line installed with this package, `chinese_postman`.  
There are several optional command line arguments, but the only required one is `edgelist`.  More on those later.  
Below we solve the CPP on the [Seven Bridges of Konigsberg] network.  This edgelist is provided in this repo, but you
can swap this edgelist CSV out for any comma delimited text file where the first two columns represent the node pairs
in your network.

```
chinese_postman --edgelist postman_problems/examples/seven_bridges/edgelist_seven_bridges.csv
```

### 2. Python

The postman solvers are modules that can also be imported and run within a Python environment.  This might interest you 
if solving the CPP is just one step in your problem, you'd like to poke and prod at the output, or you'd like to tweak 
the visualization or optimization parameters beyond what's provided from the CLI.

```python
from postman_problems.graph import cpp

# find CPP solution
circuit, graph = cpp(edgelist_filename='postman_problems/examples/seven_bridges/edgelist_seven_bridges.csv',
                     start_node='D')

# print solution
for e in circuit:
    print(e)
```

You should see output that describes the CPP solution (Eulerian circuit) through each edge.  Something like this:
```
('D', 'C', {'trail': 'g', 'distance': 3, 'id': 6})
('C', 'A', {'trail': 'c', 'distance': 2, 'id': 2})
('A', 'C', {'trail': 'd', 'distance': 10, 'id': 3})
('C', 'D', {'trail': 'g', 'distance': 3, 'id': 6, 'augmented': True})
('D', 'B', {'trail': 'f', 'distance': 9, 'id': 5})
('B', 'A', {'trail': 'a', 'distance': 3, 'id': 0})
('A', 'B', {'trail': 'b', 'distance': 5, 'id': 1})
('B', 'A', {'trail': 'a', 'distance': 3, 'id': 0, 'augmented': True})
('A', 'D', {'trail': 'e', 'distance': 1, 'id': 4})
```

## Examples

Two examples are within this repo to demonstrate the usage.

### Seven Bridges of Konigsberg

### Sleeping Giant





[Postman Problems]: https://en.wikipedia.org/wiki/Route_inspection_problem
[Seven Bridges of Konigsberg]:https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg

