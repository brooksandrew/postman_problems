[![Build Status](https://travis-ci.org/brooksandrew/postman_problems.svg?branch=master)](https://travis-ci.org/brooksandrew/postman_problems)

[![Coverage Status](https://coveralls.io/repos/github/brooksandrew/postman_problems/badge.svg?branch=master)](https://coveralls.io/github/brooksandrew/postman_problems?branch=master)


## Postman Problems:

[Contents](#contents)  
[Install](#install)  
[Usage](#usage)  
[Examples](#examples)  
[Developers](#developers)

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

There are several optional command line arguments, but the only required one is `--edgelist`.  More on those later.
  
Below we solve the CPP on the [Seven Bridges of Konigsberg] network.  The edgelist is provided in this repo, but you
can swap this out for any comma delimited text file where the first two columns represent the node pairs in your network.

```bash
chinese_postman --edgelist postman_problems/examples/seven_bridges/edgelist_seven_bridges.csv
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

The first two values of each tuple are the "from" and the "to" node respectively.  

The third value contains the edge attributes for each edge walked.  These are mostly grabbed from the starting graph, 
with two exceptions:
  - `augmented ` is added to edges after their first walk (double backing... the thing we want to minimize)
  - `id` is generated to aid computation in the case of parallel edges.  This can generally be ignored.
 
 
### 2. Python

The postman solvers are modules that can also be imported and run within a Python environment.  This might interest you 
if solving the CPP is just one step in your problem, you'd like to poke and prod at the output, or you'd like to tweak 
the visualization or optimization parameters beyond what's provided from the CLI.

The snippet below should produce exactly the same output as printed above in [CLI](#1.-cli).

```python
from postman_problems.graph import cpp

# find CPP solution
circuit, graph = cpp(edgelist_filename='postman_problems/examples/seven_bridges/edgelist_seven_bridges.csv',
                     start_node='D')

# print solution
for e in circuit:
    print(e)
```



## Examples

Two examples are included in `postman_problems` which demonstrate end-to-end usage: raw edgelist & nodelist => 
optimization and visualization.
  
Both examples are added as entry points and pre-configured arguments, so they can be executed with the single commands below.
 
Note, the visualization step will write a GIF and a series of PNGto your filesystem.  The paths are locked into the 
  *postman_problems/examples/[example_name]/output/* dir, so they should not be capable of writing rogue files on your 
  machine.

### Seven Bridges of Konigsberg

```
chinese_postman_seven_bridges
```

This will produce the `cpp_graph.svg` below:

![Alt text](./postman_problems/examples/seven_bridges/output/cpp_graph.svg)

Here's the GIF (`cpp_graph.gif`) produced by the example.  The nodes and edges in red the current direction.
 
![Alt text22](./postman_problems/examples/seven_bridges/output/cpp_graph.gif)


### Sleeping Giant

```
chinese_postman_sleeping_giant
```






[Postman Problems]: https://en.wikipedia.org/wiki/Route_inspection_problem
[Seven Bridges of Konigsberg]:https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg

