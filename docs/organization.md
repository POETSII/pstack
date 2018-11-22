### Organization

The main components of `pstack` are shown and described below.

<p align="center">
	<img align="center" src="diagram-v2.svg" width="80%" alt="Organization">
</p>

#### 1. POETS Engines

Engines are arbitrary software/hardware components capable of simulating POETS
devices as specified in the
[`graph-schema`](https://github.com/POETSII/graph_schema) spec and conforming
to an additional (simple and minimal) protocol to govern their communication
with Redis. `pstack` ships with a stand-alone POETS simulator `psim` that
doubles as a compliant engine.

The engine specification is described in [Developing `pstack`
Engines](engines.md).

#### 2. POETS Daemon ([`pd`](../pd.py))

This is a persistent background process that monitors the job queue on Redis
and spawns engines to execute accepted jobs. It handles all aspects of job and
process control (e.g. queueing, status reporting and logging).

#### 3. POETS Client ([`pcli`](../pcli.py))

A super-charged Python terminal (syntax-coloring, auto-completion and
persistent context) that serves as an entry point for users into a `pstack`
service. It allows users to:

- Connect to a `pstack` deployment
- Start a process by loading a POETS XML file from their machines
- List and control running processes (through equivalent implementations of `ps` and `kill`)
- Monitor processes and back-end infrastructure in real time (through an equivalent implementation of `top`)
- Divide application devices into multiple subsets (called "regions") and map these to different engines