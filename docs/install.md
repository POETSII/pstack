### Installation

This guide will walk you through installing `pstack` on your machine.

#### Before Installing

There are a couple of things to take note of before proceeding with the
installation.

##### 1. `pstack` is installed on Coleridge

If you're a member of the [POETS project](https://poets-project.org) and would
like to use `pstack` you can SSH into and use the `pstack` deployment on
[Coleridge](cambridge.md). This does not require setting up anything on your
own computer so it's a very easy way to get started.

##### 2. You may not need to use all `pstack` components

This repository contains [the three building blocks of `pstack`](organization.md):

- `psim`: an independent simulator and a compatible engine
- `pcli`: command-line user terminal
- `pd`: the daemon process

All three will become available once you clone this repo but you may only want
to use one or two, depending on your needs. Here are possible use cases:

1. You want to run **simple simulations** of local XML files (single-threaded and
non-distributed).
2. You want to run **distributed or multi-threaded simultions** on an existing
`pstack` deployment.
3. You want to **add your computer as an engine** to an existing `pstack` deployment.
4. You want to **deploy `pstack`** and make it available to other uses.

For (1), it will be sufficient to use `psim` as an independent tool.

(2) and (3) require that you use `pcli` and `pd` (respectively) while
forwarding local Redis traffic over an SSH tunnel to a remote `pstack`
deployment as [explained here](cambridge.md#running-pcli-locally).

(4) requires installing Redis and optionally setting up `pd` on one or several
machines.

#### Installation Steps

1. [Install pip](https://pip.pypa.io/en/stable/installing/)
2. [Install modules in `requirements.txt`](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

When setting up Python projects, it's standard practice to install
`requirements.txt` dependencies locally within the project. It's therefore
strongly recommended that you use
[`virtualenv`](https://virtualenv.pypa.io/en/latest/) for step 2.

You may want to place symlinks to the wrappers in `bin` in your `/usr/bin` to
make `pcli`, `pd` and `psim` available globally. Note that the wrapper require
a `virtualenv` environment to be setup up in the repository directory.

If you're deploying `pstack` as a service to other users (use case 4), you'll
also need to install Redis. Redis is available as an
[Ubuntu package](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04) and can also be instantiated as a [docker container](https://hub.docker.com/_/redis/).
