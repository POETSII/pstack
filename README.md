## POETS Simulator (PSIM)

### Overview

This is a barebone simulator for POETS applications.

#### Usage

```
Usage:
  psim.py [options] <app.xml>

Options:
  -d --debug            Print debug information.
  -l --level=<n>        Specify log messages verbosity [default: 1].
  -t --temp=<dir>       Specify simulation file directory [default: /tmp].
  -g --region=<n>       Specify simulation region [default: 0].
  -m --map=<file.json>  Load device map from file.
  -r --result           Print simulation result as JSON object.
  -q --quiet            Suppress all outputs (except --result).
```
