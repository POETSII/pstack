## POETS Simulation Stack (`pstack`)

<p align="center">
	<img align="center" src="docs/pstack.svg" width="40%" alt="PSIM Setup">
</p>

### Overview

`pstack` is a distributed [POETS](https://poets-project.org) simulation stack
based on [Redis](http://redis.io/). It exposes the compute power of a
hetrogeneous array of POETS back-end engines to multiple users in a POSIX-like
environment.

Features:

- **Processes**: application instances modeled after POSIX [processes](docs/pcli.md#processes)
- **Multi-user support**: multiple users can run processes on a single `pstack` service simultaneously
- **Distributed execution**: a single application can be [distributed across several machines in arbitrary arrangements](docs/engines.md#simulation-regions)
- **Real-time Monitoring**: [live monitor](docs/pcli.md#the-process-viewer) of running processes and back-end engine resource utilisation
- **Heterogeneity**: supports [arbitrary back-end engines](docs/engines.md#what-is-an-engine) (e.g. different simulators or even actual hardware)
- **Job queues**: processes are queued when back-end engines are unavailable or insufficient
- **Terminal**: [command line user interface](docs/pcli.md) with built-in Python interpreter
- **Debugging**: supports debug breakpoints and manual inspection/injection of messages
- **Unit Testing**: Down-to-earth [unit testing framework](tests) supporting push-button testing over entire back-end infrastructure
- **Minimal dependencies**: just [pip](https://pip.pypa.io/en/stable/installing/) and [socat](https://www.howtoinstall.co/en/ubuntu/xenial/socat) on a fresh Ubuntu installation.
- **Automated Deployment**: parallel (multi-host) installation over SSH in 10 seconds using [fabric](https://www.fabfile.org/).

Design Goals:

- Focus on developing POETS-specific capabilities while leaving more common
programming chores to existing specialized tools and technologies
([Redis](http://redis.io/) for distributed shared memory and
[socat](https://linux.die.net/man/1/socat) for socket communication).
- Decouple stack layers using TCP connections to permit reliable,
performant and secure distributed operation using standard communication
technologies (Ethernet, SSH tunnels etc.).
- Leverage Python for productivity
([multiprocessing](https://docs.python.org/2/library/multiprocessing.html),
[jinja](http://jinja.pocoo.org/docs/2.10/)) and C for performance
([simulation](templates))
- Deliver the best performance and feature set while keeping the
implementation as simple and maintainable as possible.

### Documentation

#### Design Notes

- [Stack Organization](docs/organization.md)

#### User Guides

- [Using `psim`](docs/psim.md) (standalone simulations)
- [Using `pcli`](docs/pcli.md) (distributed simulations)
- [Cambridge `pstack` Deployment](docs/cambridge.md)

#### Developer Guides

- [Programming with `pstack`](docs/programming.md)
- [Developing `pstack` Engines](docs/engines.md)
