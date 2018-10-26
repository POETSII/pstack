#!/usr/bin/env python

import json
import redis
import random
import docopt
import datetime
import subprocess

from multiprocessing import Queue
from multiprocessing import Process

from psim import psim
from simple_redis import pop_json
from simple_redis import push_json


usage="""POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of workers (core count by default).
  -n --name=<name>   Specify engine name (hostname by default)
  -h --host=<host>   Specify Redis host [default: localhost].
  -p --port=<port>   Specify Redis port [default: 6379].
  -q --quiet         Suppress all outputs.

"""


def log(msg):
    now = datetime.datetime.utcnow()
    dt_str = now.strftime("%y-%m-%d %H:%M")
    print "%s - %s" % (dt_str, msg)


def parse_connection_str(con_str):
    """Parse connection string in the form host:port."""
    try:
        host_str, port_str = con_str.split(':')
        return (host_str, int(port_str))
    except ValueError:
        raise Exception("Could not parse '%s'" % con_str)


def start_workers(engine_name, nworkers, host, port):

    redis_cl = redis.StrictRedis(host, port)

    queue = Queue()
    worker_busy = [0] * nworkers

    def create_worker(index):
        args = (redis_cl, queue, index, host, port, engine_name)
        return Process(target=run_worker, args=args)

    workers = map(create_worker, range(nworkers))

    for worker in workers:
        worker.start()

    def publish_s():
        nused = sum(worker_busy)
        publish_state(redis_cl, engine_name, nworkers, nused)

    publish_s()

    def process_queue_item():

        worker_index, item_type, item = queue.get()

        if item_type == "msg":
            log("[Worker %d] %s" % (worker_index, item))
        elif item_type == "busy":
            worker_busy[worker_index] = item
            publish_s()
        else:
            raise Exception("Unrecognized queue item type")

    while True:
        try:
            process_queue_item()
        except Exception:
            pass
        except KeyboardInterrupt:
            break


def run_worker(redis_cl, queue, index, host, port, engine_name):
    """Wait for and process jobs from Redis "jobs" queue."""

    def log_local(msg):
        """Print message to local daemon log."""
        queue.put((index, "msg", msg))

    def set_busy(busy):
        """Inform parent thread of an update to the worker's busy state."""
        queue.put((index, "busy", 1 if busy else 0))

    def log_redis(job, msg):
        """Print message to redis job queue."""
        if job.get("verbose"):
            queue = job["result_queue"]
            push_json(redis_cl, queue, "[%s] %s" % (engine_name, msg))

    log_local("Waiting for jobs ...")

    while True:
        try:
            job = pop_json(redis_cl, "jobs")
        except KeyboardInterrupt:
            break

        msg = "Starting %(name)s (region %(region)s) ..." % job

        log_local(msg)
        log_redis(job, msg)
        set_busy(True)
        redis_cl.sadd("running", job["name"])

        options = {
            "level": 0,
            "host": host,
            "port": port,
            "quiet": True,
            "debug": False,
            "force_socat": True,
            "regions": [job["region"]]
        }

        result = psim(job["xml"], job["region_map"], options)

        log_redis(job, "Finished %(name)s (region %(region)s)" % job)
        push_json(redis_cl, job["result_queue"], result)
        new_completed = redis_cl.incr(job["completed"])
        if new_completed == job["nregions"]:
            redis_cl.srem("running", job["name"])
        set_busy(False)
        log_local("Completed")


def get_capabilities(name=None, nworkers=None):
    """Get hostname and core count using 'hostname' and 'nproc'.

    Inputs:
      - name     (str): an *override value*
      - nworkers (str): an *override value*

    Returns:
      - (name, workers) tuple of type (str, int)

    These are obtained by running the tools 'hostname' and 'nproc'.
    """

    def run_command(cmd):
        """Run command and return output, or None if command fails."""
        run = subprocess.check_output
        try:
            return run(cmd, shell=True, stderr=subprocess.PIPE).strip()
        except Exception:
            return None

    def get_rand_name():
        return "unnamed-%s" % "".join(random.sample("0123456789", 6))

    name = name or run_command("hostname") or get_rand_name()
    nworkers = int(nworkers or run_command("nproc") or "1")

    return (name, nworkers)


def publish_state(redis_cl, name, nworkers, nused):
    """Publish engine information and current state.

    Information is stored in redis using client name as key.
    """

    resource_str = "%d threads" % nworkers if nworkers>1 else "1 thread"
    usage_str = "%.1f%%" % (nused / float(nworkers) * 100)

    engine_information = {
        "name": name,
        "type": "Simulator (psim)",
        "resources": resource_str,
        "_nresources": nworkers,
        "usage": usage_str,
        "_nused": nused
    }

    redis_cl.client_setname(name)
    redis_cl.set(name, json.dumps(engine_information))


def main():
    args = docopt.docopt(usage, version="v0.1")
    name, nworkers = get_capabilities(args["--name"], args["--workers"])
    log("Starting (Engine %s)..." % name)
    start_workers(name, nworkers, args["--host"], int(args["--port"]))
    log("Shutting down ...")


if __name__ == '__main__':
    main()
