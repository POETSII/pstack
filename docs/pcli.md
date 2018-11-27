### Using `pcli`

`pcli` is a terminal that allows users to run distributed POETS applications
and manage a `pstack` deployment. This manual provides an overview of `pcli`
and some usage examples.

#### Content

- [Usage](#usage)
- [The Basics](#the-basics)
- [Quick Start](#quick-start)
- [Processes](#processes)
- [The Process Viewer](#the-process-viewer)
- [Starting a Process](#starting-a-process)
- [Process Management](#process-management)

#### Usage

```
POETS Client (pcli) v0.1

Usage:
  pcli.py [options]

Options:
  -n --nocolor   Disable terminal colors.
  -q --quiet     Suppress printing banner.
```

#### The Basics

`pcli` is built on top of a Python interpreter; commands are implemented as
Python functions and are called using Python's syntax. All of Python, its
standard library modules and package ecosystem are available as well. For
example ...

```
$ pcli --quiet
pcli> [x**2 for x in range(10)]
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
pcli> from datetime import datetime
pcli> datetime.now()
datetime.datetime(2018, 11, 26, 14, 21, 57, 46882)
pcli>
```

In other words, `pcli` is essentially the same as the off-the-shelve Python
interpreter available on most systems but with built-in `pstack` functions
(that are in fact imported from the module [`interactive.py`](../py/interactive.py)).

To improve user experience, `pcli` features syntax colouring, fish-like [autosuggestions](https://fishshell.com/docs/current/tutorial.html#tut_autosuggestions) and
[persistent context](http://docs.http-prompt.com/en/latest/user-guide.html#persistent-context). Variables of basic data types and command history are retained between
sessions.

#### Quick Start

You can run a simulation on `pcli` using the `run` command as follows:

```
pcli> run("tests/ring-oscillator-01.xml")
{'states': {u'n0': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n1': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n2': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n3': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}}, 'metrics': {u'Exit code': 0, u'Delivered messages': 40}}
```

(here loading one of the files from the repo's `test` directory)

Notice that the output is in the [machine-friendly format of
`psim`](psim.md#output-formats), specifically a JSON object containing
simulation metrics and final device states. The above is therefore very
similar to invoking `psim` (with the `--quiet` and `--result` switches) but
with the crucial difference that it's been executed by one of the engines
connected to the `pstack` deployment in use.

#### Processes

One of the design goals of `pstack` is to provide a desktop-like POETS
environment. To this end, some concepts are burrowed from POSIX including the
notion of a process as an instance of an executable binary. In `pstack`, a
_process_ is an in-memory instance of a POETS XML application.

Processes are in one of two states:

1. _Waiting_: the process is held in memory but awaits the availability of
a sufficient number of suitable engines to start.

2. _Running_: the process has started; its
[regions](engines.md#simulation-regions) are all being simulated by suitable
engines.

#### The Process Viewer

Before delving into more commands and  usage scenarios, it's probably a good
idea to introduce one of the main features of `pcli`, _the process viewer_, a
full-screen real-time process and resource monitor in the spirit of `top`.
Here's what it looks like ...

<p align="center">
	<img src="pcli-top.png"/>
</p>

This tool can be started by typing `top` in `pcli`. It shows available engines
(three in this case), their resource utilization plus a process table. Changes
in the process table or engine availability/utilization are updated in
real-time.

Having a separate instance of `pcli` with the process viewer running may be
helpful to visualize what happens when following the remaining steps in this
guide.

#### Starting a Process

As shown in [Quick Start](#quick-start), the command `run` is used to start
processes. Here are more ways to use `run` ...

##### The `async` Switch

With no additional arguments other than the XML file, `run` will block until
the process terminates then return a simulation result object. This behavior
can be changed by passing `async=True` which will make `run` return
immediately with a pending computation result called _a future_ (read [this
article](https://en.m.wikipedia.org/wiki/Futures_and_promises) for background
if you're unfamiliar with futures). The future object can be blocked on using
the function `block` to return the simulation result.

Here's an example ...

```
pcli> future = run("tests/ring-oscillator-01.xml", async=True)
pcli> 1 + 2
3
pcli> block(future)
{'states': {u'n0': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n1': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n2': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n3': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}}, 'metrics': {u'Exit code': 0, u'Delivered messages': 40}}
```

This mechanism allows users to start processes and move on to do other things
while the process executes (in the unimaginative example above the user
evaluates `1 + 2`).

##### The `verbose` Switch

Application and [`pd`](organization.md#2-poets-daemon-pd) log messages can be
printed during execution by passing `verbose=True` to `run`. Here's an example
...

```
pcli> run("tests/ring-oscillator-01.xml", verbose=True)
[byron.cl.cam.ac.uk] Starting 6177 (region 0) ...
[byron.cl.cam.ac.uk] Region 0 -> Log [device n0, level 1]: counter = 1
[byron.cl.cam.ac.uk] Region 0 -> Log [device n1, level 1]: counter = 1
[byron.cl.cam.ac.uk] Region 0 -> Log [device n2, level 1]: counter = 1
[byron.cl.cam.ac.uk] Region 0 -> Log [device n3, level 1]: counter = 1
(log messages truncated for brevity)
[byron.cl.cam.ac.uk] Region 0 -> Log [device n0, level 1]: counter = 10
[byron.cl.cam.ac.uk] Region 0 -> Log [device n1, level 1]: counter = 10
[byron.cl.cam.ac.uk] Region 0 -> Log [device n2, level 1]: counter = 10
[byron.cl.cam.ac.uk] Region 0 -> Log [device n3, level 1]: counter = 10
[byron.cl.cam.ac.uk] Region 0 -> Exit [device n0]: handler_exit(0) called
[byron.cl.cam.ac.uk] Region 0 -> Metric [Delivered messages]: 40
[byron.cl.cam.ac.uk] Region 0 -> Metric [Exit code]: 0
[byron.cl.cam.ac.uk] Region 0 -> State [n0]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n1]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n2]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n3]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Finished 6177 (region 0) ...
{'states': {u'n0': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n1': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n2': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n3': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}}, 'metrics': {u'Exit code': 0, u'Delivered messages': 40}}
```

Here, the simulation has been picked up by engine `byron.cl.cam.ac.uk`. The
lines prefixed with

`[byron.cl.cam.ac.uk] Region 0 -> `

are intermediate engine outputs (in this case, the [human-friendly output of
`psim`](psim.md#output-formats)) while other lines such as

```
[byron.cl.cam.ac.uk] Starting 6177 (region 0) ...
[byron.cl.cam.ac.uk] Finished 6177 (region 0) ...
```

are `pd` outputs.

##### Log Message Verbosity `level`

The maximum log level for applications can be specified by passing the `level`
argument to `run` (the default log level is 1). For example ...

```
pcli> run("tests/ring-oscillator-01.xml", verbose=True, level=0)
[byron.cl.cam.ac.uk] Starting 4 (region 0) ...
[byron.cl.cam.ac.uk] Region 0 -> Exit [device n0]: handler_exit(0) called
[byron.cl.cam.ac.uk] Region 0 -> Metric [Delivered messages]: 40
[byron.cl.cam.ac.uk] Region 0 -> Metric [Exit code]: 0
[byron.cl.cam.ac.uk] Region 0 -> State [n0]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n1]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n2]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Region 0 -> State [n3]: state = 0, counter = 10, toggle_buffer_ptr = 0
[byron.cl.cam.ac.uk] Finished 4 (region 0) ...
{'states': {u'n0': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n1': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n2': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n3': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}}, 'metrics': {u'Exit code': 0, u'Delivered messages': 40}}
```

The above example shows a useful trick whereby setting `level=0` suppresses
application log messages, leaving only engine and `pd` outputs. Notice that
specifying `level` without using `verbose=True` is meaningless (since log
messages won't be collected in the first place).

_Note on performance_: log messages are relayed through a high-level
slow-performance interface and will therefore slow processes considerably.
It's therefore recommended that you pass `verbose=True` only when debugging.

#### Process Management

At the moment, `pstack` does not support many ways to interact with a process
_after_ it has been started ([Application
Engines](programming.md#application-engines) are a powerful mechanism to
manipulate processes but they must be hooked in during process creation).

Processes can be killed using the command `kill` which takes the process
identifier (PID) as a single argument. The PID can be retrieved from the
future object, here's how ...

```
pcli> future = run("tests/ring-oscillator-01.xml", async=True)
pcli> kill(future.pid)
```

Explicit PIDs can be passed to `kill` too (for example by looking up processes
in the [process viewer](#the-process-viewer), or through the command `ps`
which returns a list of current process PIDs). However, this is discouraged as
it may affect other users.

(work in progress)
