## Developing `pstack` Engines

### Content

- [What is an Engine?](#what-is-an-engine)
- [How does an Engine Work?](#how-does-an-engine-work)
- [Distributed Simulations](#distributed-simulations)
	- [Simulation Regions](#simulation-regions)
	- [Engine Communication](#engine-communication)

### What is an Engine?

Engines are the bottom layer of `pstack` and are responsible for computing
device states and consuming/generating messages. This document describes the
`pstack` engine specification.

The diagram below is a more refined view of the organization diagram in
[README](../readme.md), showing how engines communicate with their surrounding
components in `pstack`.

<p align="center">
	<img align="center" src="engine.svg" width="75%">
</p>

This may appear somewhat complicated by it's not. Well, here are the good news
for a start:

1. Engines communicate with their environment through input and output
streams. Even though they're building blocks for a distributed computing
stack, engines are not required to perform any network communication at all
and their only interfaces to the world are good old `printf` and `scanf`.

2. Engines are spawned and given processing job details by other parts of the
stack (specifically, by the daemon process `pd`) meaning that they don't need
to worry about service-level concerns such as persistence. An engine is a
processing tool used by `pd` to expose a persistent service.

### How does an Engine Work?

Before delving into the spec, it's probably a good idea to start with a
simplified description of how engines work within `pstack`, to develop some
background intuition and make understanding the details easier.

As you're probably aware from [README](../readme.md), `pstack` uses
[Redis](https://redis.io/), a distributed in-memory data structure server, to
relay messages and process information between daemon (`pd`) and client
(`pcli`) instances running on different machines. Simulation jobs are started
using the `run` command in `pcli` as follows:

```javascript
pcli> run("application.xml")
```

Here's what happens after this command is executed:

1. `pcli` reads `application.xml` and pushes its content to the Redis queue
`jobs`.

2. An instance of `pd` deques the job and spawns an engine to process it,
passing it the job's XML string and connecting its streams as shown in the
diagram above. Here, `pd` redirects the engine's `stdout` and `stderr` streams
to itself while hooking its `stdin` and a custom stream (`fd3`, more on this
later) to [`socat`](https://linux.die.net/man/1/socat), a versatile tool that
can relay standard streams to a TCP connection.

3. The engine runs, reading from `stdin` and printing to `fd3` messages
from/to external devices. These are communicated through `socat` to message
transfer queues on Redis.

4. Some time later, the engine terminates and prints final device states plus
some execution statistics to `stdout`. This output is captured by `pd` and
pushed to a _results_ queue on Redis. It is subsequently dequed by the `pcli`
instance that created the job and displayed to the user as shown below (more
on output format later).

```javascript
pcli> run("application.xml")
{'states': {u'n0': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n1': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n2': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}, u'n3': {u'state': 0, u'counter': 10, u'toggle_buffer_ptr': 0}}, 'metrics': {u'Exit code': 0, u'Delivered messages': 40}, 'log': [[u'n0', 1, u'counter = 1'], [u'n1', 1, u'counter = 1'], [u'n2', 1, u'counter = 1'], [u'n3', 1, u'counter = 1'], [u'n0', 1, u'counter = 2'], [u'n1', 1, u'counter = 2'], [u'n2', 1, u'counter = 2'], [u'n3', 1, u'counter = 2'], [u'n0', 1, u'counter = 3'], [u'n1', 1, u'counter = 3'], [u'n2', 1, u'counter = 3'], [u'n3', 1, u'counter = 3'], [u'n0', 1, u'counter = 4'], [u'n1', 1, u'counter = 4'], [u'n2', 1, u'counter = 4'], [u'n3', 1, u'counter = 4'], [u'n0', 1, u'counter = 5'], [u'n1', 1, u'counter = 5'], [u'n2', 1, u'counter = 5'], [u'n3', 1, u'counter = 5'], [u'n0', 1, u'counter = 6'], [u'n1', 1, u'counter = 6'], [u'n2', 1, u'counter = 6'], [u'n3', 1, u'counter = 6'], [u'n0', 1, u'counter = 7'], [u'n1', 1, u'counter = 7'], [u'n2', 1, u'counter = 7'], [u'n3', 1, u'counter = 7'], [u'n0', 1, u'counter = 8'], [u'n1', 1, u'counter = 8'], [u'n2', 1, u'counter = 8'], [u'n3', 1, u'counter = 8'], [u'n0', 1, u'counter = 9'], [u'n1', 1, u'counter = 9'], [u'n2', 1, u'counter = 9'], [u'n3', 1, u'counter = 9'], [u'n0', 1, u'counter = 10'], [u'n1', 1, u'counter = 10'], [u'n2', 1, u'counter = 10'], [u'n3', 1 , u'counter = 10']]}
pcli>
```

### Distributed Simulations

The above subsection described a scenario where a simulation job is picked up
and processed by a single engine. Point 2 described how messages are sent and
received from "external devices" by relaying `stdin` and `fd3` through `socat`
to Redis. This in fact only relevant to distributed (multi-engine) simulations.

#### Simulation Regions

`pstack` supports distributed simulations by splitting POETS applications into
multiple device subsets called **Regions** and assigning each to an engine. An
_external device_ is any device that doesn't belong to the engine's allocated
region.

Note that `pstack` uses a more general definition of external devices compared
to `graph-schema`. In `pstack`, an external device is any device that's
outside the engine's region, whether defined as a `<DevI>` or an `<ExtI>`
element.

#### Engine Communication

This subsection will walk through an example distributed simulation to explain
how multiple engines interact.

<p align="center">
	<img align="center" src="regions.svg" width="75%">
</p>

The diagram above depicts a simulation of ring-oscillator application that's
split across three engines.

As a start, here's how the application itself behaves. After initialization,
device `n0` send a message and increments a state counter. The message is then
relayed by subsequent nodes across the loop back to `n0` and the process is
repeated until the counter at `n0` reaches a certain value. Device `n0` then
terminates the application by calling `handler_exit(0)`.

The distributed simulation starts when the user executes the `run` command on
`pcli`. In this case, the user passes an additional parameter to `run` which
breaks the simulation into three jobs, here's how ...

```javascript
pcli> run(xml2, rmap={"n0": 0, "n5": 0, "n1": 1, "n4": 1, "n2": 2, "n3": 2})
```

The parameter `rmap` is a **region map**. It's a mapping between device names
and regions, identified as non-negative integers.

After executing `run`, `pcli` pushes three simulation jobs to Redis,
corresponding to the regions `0`, `1` and `2`. These get subsequently dequed
by three `pd` instances, each receiving copies of the application's XML string
and the region map. The `pd` instances now launch three engines, each
responsible for simulating a single application region as shown in the
diagram.

From here on, things are somewhat straightforward. Each engine knows its
allocated region so it can tell which devices are local vs. external from its
perspective. It starts an event loop to process messages and update (local)
device states. Any time a local device generates a message that fans out to
devices in a remote region, the engine pushes it to a dedicated region queue
on Redis. The engine responsible for simulating the remote region then deques
and processes the transmitted message. For example, when `n0` sends a message
to `n1`, Engine 0 pushes this to Queue 1 where it's picked up by Engine 1.
Here are the actual mechanics underlying this transfer:

1. Engine 0 prints a Redis [push command](https://redis.io/commands/rpush) to
add the tuple (source device, source pin, message fields) to Queue 1. This
command is printed to `fd3` and relayed to Redis by `socat`.

2. Engine 1 prints a Redis [pop command](https://redis.io/commands/blpop) to
its `fd3` when it finishes processing local messages. It then block-reads on
`stdin` which receives (via `socat`) any items pushed to Queue 1. The tuple
pushed by Engine 0 is then read by Engine 1.

3. Engine 1 looks up which local devices are destinations of the originating
device and pin specified in the tuple (in this case just `n1`) and calls their
receive handlers to process the message.

You may be able to see that things are somewhat simple from an engine
programmer's point of view. Messages to remote destinations should be printed
with `printf` (to `fd3`) and, when there are no local messages to process,
just wait for incoming messages with `scanf` :relieved:

This leaves application termination and the collection of simulation results.
These are straightforward too; when device `n0` calls `handler_exit(0)` this
pushes a special _application end_ symbol on the queues of all other regions,
forcing all engines to terminate their event loops and print local device
states to `stdout`. These are then picked up by the parent `pd` processes and
pushed to a _results_ queue dedicated to the simulation. The content of this
queue are dequeued and combined by `pcli`, which then prints simulation
results to the user.
