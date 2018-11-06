## Developing `pstack` Engines

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
to worry about service-level concerns such as persistence or availability. An
engine is a processing tool which `pd` uses to expose a persistent service.

### How do Engines Work?

Before delving into the spec, it's probably a good idea to start with a
simplified description of how engines work within `pstack`, mainly to develop
some background intuition which will make understanding the details easier.

As you're probably aware from a quick glance at [README](../readme.md),
`pstack` uses Redis as a communication infrastructure to relay messages and
process/job information between daemon (`pd`) and client (`pcli`) processes on
different machines. [Redis](https://redis.io/) is a distributed shared memory
server that allows processes on different machines to store and access various
data structures (e.g. dictionaries, lists, sets and queues). For simplicity,
we can assume that a processing _job_ is a POETS XML string which a user has
pushed to a Redis queue named `jobs` through `pcli`. Here's what happens
afterwards:

1. An instance of `pd`, which is running on some machine and monitoring the
`jobs` queue, deques the job and spawns an engine as a subprocess, passing it
the job's XML string and connecting its streams as shown in the diagram above.
Here, `pd` redirects the engine's `stdout` and `stderr` streams to itself
while hooking its `stdin` and a custom stream (`fd3`, more on this in a bit)
to `socat`, a tool which relays standard stream data to a TCP connection.

2. The engine runs, reading from `stdin` and printing to `fd3` messages
from/to external devices. These are communicated through `socat` to Redis.

3. The engine terminates and prints final device states plus some execution
statistics to `stdout`. This output is captured by `pd` and pushed to a
_results_ queue on Redis. It's subsequently dequed by the `pcli` instance that
created the job and displayed to the user.

### Regions

Point 2 in the previous subsection mentioned that engines can send and receive
messages from/to "external devices". `pstack` supports distributed simulations
by splitting POETS applications into multiple device subsets called _Regions_
and assigning each to an engine. An "external device" is any device that
doesn't belong to the engine's allocated region.

