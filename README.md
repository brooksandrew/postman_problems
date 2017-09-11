[![Build Status](https://travis-ci.org/brooksandrew/postman_problems.svg?branch=master)](https://travis-ci.org/brooksandrew/postman_problems)

[![Coverage Status](https://coveralls.io/repos/github/brooksandrew/postman_problems/badge.svg?branch=master)](https://coveralls.io/github/brooksandrew/postman_problems?branch=master)

### Contents

This package contains implementations to solve the suite of [Postman Problems] from graph theory.

Currently a suite of 1: The Chinese Postman Problem, the most straightforward of the Postman Problems.

The Rural Postman Problem will be added next.


### Usage

Install the `postman_problems` package:

```
pip install postman_problems
```

Run one of the provided examples:

```
python examples/sleepinggiant/cpp.py
```

You should see output that describes the CPP solution (Eulerian circuit) through each trail on the Sleeping Giant graph that looks something like this:

```
('b_end_east', 'b_y', {'distance': 1.32, 'trail': 'b', 'estimate': 0.0, 'weight_flipped': -1.32, 'weight': 1.32, 'augmented': True})
('b_y', 'b_o', {'distance': 0.08, 'trail': 'b', 'estimate': 0.0, 'weight_flipped': -0.08, 'weight': 0.08, 'augmented': True})
('b_o', 'b_gy2', {'distance': 0.05, 'trail': 'b', 'estimate': 1.0, 'weight_flipped': -0.05, 'weight': 0.05, 'augmented': True})
('b_gy2', 'w_gy2', {'distance': 0.03, 'trail': 'gy2', 'estimate': 1.0, 'weight_flipped': -0.03, 'weight': 0.03, 'augmented': True})
('w_gy2', 'g_gy2', {'distance': 0.05, 'trail': 'gy2', 'estimate': 0.0, 'weight_flipped': -0.05, 'weight': 0.05, 'augmented': True})
('g_gy2', 'park_east', {'distance': 0.14, 'weight_flipped': -0.14, 'trail': 'g', 'estimate': 0.0, 'weight': 0.14})
('park_east', 'b_o', {'distance': 0.11, 'weight_flipped': -0.11, 'trail': 'o', 'estimate': 0.0, 'weight': 0.11})
('b_o', 'b_y', {'distance': 0.08, 'weight_flipped': -0.08, 'trail': 'b', 'estimate': 0.0, 'weight': 0.08})
('b_y', 'park_east', {'distance': 0.14, 'weight_flipped': -0.14, 'trail': 'y', 'estimate': 0.0, 'weight': 0.14})
('park_east', 'w_gy2', {'distance': 0.12, 'weight_flipped': -0.12, 'trail': 'w', 'estimate': 0.0, 'weight': 0.12})
...
```


[Postman Problems]: https://en.wikipedia.org/wiki/Route_inspection_problem

