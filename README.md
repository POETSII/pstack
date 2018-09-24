## POETS Simulator (`psim`)

### Overview

`psim` is a distributed simulator for POETS applications that uses
[Redis](http://redis.io/) as an orchestration layer.

#### Usage

```
Usage:
  psim.py [options] <app.xml>

Options:
  -d --debug            Print debug information.
  -l --level=<n>        Specify log messages verbosity [default: 1].
  -t --temp=<dir>       Specify simulation file directory [default: /tmp].
  -m --map=<file.json>  Load device map from file.
  -r --result           Print simulation result as JSON object.
  -q --quiet            Suppress all outputs (except --result).
```

#### Requirements

The tool requires Python 2 and
[`pip`](https://pip.pypa.io/en/stable/installing/). For distributed
simulations, [`socat`](https://linux.die.net/man/1/socat) is needed too.

#### Documentation

- [Getting Started](docs/getting-started.md)
- [How it works](docs/how-it-works.md)
