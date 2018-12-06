### Cambridge `pstack` Deployment

If you're a member of the POETS project, you can access the [POETS Cloud
VMs](https://github.com/POETSII/poets-cloud) hosted at Cambridge University.
`pstack` has been deployed on few of these and is ready for use without
requiring anything to be installed locally on your computer.

#### Deployment Information

The deployment consists of a Redis instance running on

- `coleridge.cl.cam.ac.uk`

and three `pd` instances running on

- `byron.cl.cam.ac.uk` (28 cores)
- `aesop.cl.cam.ac.uk` (12 cores)
- `coleridge.cl.cam.ac.uk` (12 cores).

Each one of the three machines has local installations of the entire `pstack`
tool suite, but application tools (`psim` and `pcli`) are maintained only on
Coleridge.

#### Getting Started

The easiest way to use `pstack` is to SSH into Coleridge (follow the
instructions [here](https://github.com/POETSII/poets-cloud) to request access).

The tools `psim` and `pcli` are available to all users on Coleridge and do not
require any setup. You can get started immediately after login using the
respective user guides:

- [Using `psim`](psim.md) (standalone simulations)
- [Using `pcli`](pcli.md) (distributed simulations)

#### Running `pcli` Locally

Instead of running `pcli` on Coleridge, you may want to run it on your own
computer, so you can load local XML files, run Python scripts, write
simulation/benchmark results to disk or else. Luckily, this is very easy:

1. Install `pstack` locally
2. Open an [SSH
tunnel](https://www.howtogeek.com/168145/how-to-use-ssh-tunneling/) to forward
the local Redis port (6379) to Coleridge
3. Run and use `pcli` :tada:

Using `pcli` in this manner is possible because Redis is the central ingress
point of a `pstack` deployment (see [Organization](organization.md)).
Forwarding local Redis traffic to a remote host will therefore make that
deployment accessible to local instances of `pcli`.

#### Running `pd` Locally

Forwarding the local Redis port (6379) also makes it possible to add your own
computer as an engine to the `pstack` deployment on Coleridge. After opening
the SSH tunnel, simply run `pd` and your computer will be immediately
available as an engine for all users. You can confirm this by looking at the
engines section in the [process viewer](pcli.md#the-process-viewer).

`pd` will use your computer's hostname as an engine name by default. It will
also spawn `n` worker threads where `n` is the number of cores you have. These
settings can be changed by passing command line arguments to `pd`, here's the
usage string for reference:

```
POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of workers (core count by default).
  -n --name=<name>   Specify engine name (hostname by default)
  -h --host=<host>   Specify Redis host [default: localhost].
  -p --port=<port>   Specify Redis port [default: 6379].
  -q --quiet         Suppress all outputs.
```

As you can see, it's also possible to specify the Redis host and port. You may
be wondering why not use `--host` to point `pd` (and `pcli`) to
`coleridge.cl.cam.ac.uk` instead of forwarding ports over SSH. There are two
reasons for this:

1. The Redis port on Coleridge is not exposed publicly to the Internet and so
external connections will be blocked.

2. Redis traffic is not encrypted so forwarding it through an SSH tunnel
provides an encryption layer to secure exchanged data. This is good practice
to adhere to when using remote deployments even if the Redis port is
accessible publicly.

One thing to keep in mind when running `pd` locally is that traffic between
your computer and the Cambridge machines will be significantly slower so
simulations will take longer. If you care about performance you can use
[region constraints](pcli.md#constraining-region-mapping) to make sure that
multi-region simulations are constrained to individual machines.
