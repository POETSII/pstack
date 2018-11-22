### Programming with `pstack`

While `pstack` is essentially a tool to _run_ POETS applications, it is also
an environment to _develop_ applications. The stack plays nicely with
application generation tools developed at Newcastle
([`pml`](https://github.com/POETSII/pml/blob/master/pml.py) and
[`gml`](https://github.com/POETSII/pml/blob/master/gml.py)) and introduces new
features aimed at improving programming productivity.

#### Application Engines

`pstack` is back-end agnostic and can run POETS applications on top of
anything that can compute the state of POETS devices, usually a
high-performance simulator such as [`psim`](psim.py) or actual POETS hardware.
Through [`pcli`](pcli.py), however, users can also load and use lightweight
application-specific engines that they developed as part of their
applications. These, like other engines, would be tasked with simulating a
subset of devices in the user's application. However, they differ from
conventional engines in two important aspects:

1. They run locally on the user's machine (specifically within `pcli`), and
2. They are developed in Python! :tada:

Application engines may be slower than dedicated general-purpose engines but
they permit powerful manipulations of POETS processes with several end goals
in mind:

- **Flexible IO**: they can implement various high-level interfaces to feed
data in and out of a POETS process from
[files](http://docs.python-requests.org/en/master/),
[databases](https://postgres-py.readthedocs.io/en/latest/), [web
services](http://docs.python-requests.org/en/master/) and all sorts of other
channels.

- **Debugging Breakpoints**: they can suspend the execution of a POETS process
when certain conditions are met, allowing users to inspect local message
buffers and debug problematic execution scenarios.

- **Productivity**: they make it possible to leverage high-level programming
productivity to develop POETS applications.

For a real-life example of an application engine in action see
[`example-engine.py`](example-engine.py).