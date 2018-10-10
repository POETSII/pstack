#!/usr/bin/env python

import json
import psim
import redis
import random
import docopt
import datetime

usage="""POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of POETS workers [default: 1].
  -r --redis=<host>  Specify Redis host [default: localhost:6379].
  -n --name=<name>   Use given engine name [instead of a random name].
  -q --quiet         Suppress all outputs.

"""


def log(msg):
    now = datetime.datetime.utcnow()
    dt_str = now.strftime("%y-%m-%d %H:%M")
    print "%s - %s" % (dt_str, msg)


def _psim(xml, region_map, region):
    """Run PSIM simulation."""
    options = {"debug": False, "level": 0}
    markup = psim.parse_poets_xml(xml)
    code, _ = psim.generate_code(markup, options, region_map)
    result = psim.simulate(code, quiet=True, use_socat=True, regions=[region])
    return result


def fetch_job(redis_cl):
    """Retrieve job from Redis "jobs" queue."""
    json_str = redis_cl.blpop("jobs")[1]
    job = json.loads(json_str)
    return job


def parse_connection_str(con_str):
    """Parse connection string in the form host:port."""
    try:
        host_str, port_str = con_str.split(':')
        return (host_str, int(port_str))
    except ValueError:
        raise Exception("Could not parse '%s'" % con_str)


def wait_jobs(redis_cl):
    """Wait for and process jobs from Redis "jobs" queue."""
    while True:
        job = fetch_job(redis_cl)
        log("Running %s (region %s) ..." % (job["name"], job["region"]))
        result = _psim(job["xml"], job["region_map"], job["region"])
        result_str = json.dumps(result, indent=4)
        redis_cl.rpush(job["result_queue"], result_str)
        log("Completed" )


def run_interruptable(fun, exit_msg):
    """Call function and catch keyboard interrupt."""
    try:
        fun()
    except KeyboardInterrupt:
        log(exit_msg)


def register_engine(redis_cl, name, nworkers):
    """Register engine.

    Stores engine name and other information using client name as key.
    """

    if not name:
        # Generate random name in the form "unnamed-<6 random digits>"
        digits = "0123456789"
        name = "unnamed-%s" % "".join(random.sample(digits, 6))

    engine_information = {
        "name": name,
        "type": "Simulator (psim)",
        "resources": "%d cores" % nworkers if nworkers>1 else "1 core"
    }

    redis_cl.client_setname(name)
    redis_cl.set(name, json.dumps(engine_information))

    return name


def main():
    args = docopt.docopt(usage, version="v0.1")
    host, port = parse_connection_str(args["--redis"])
    redis_cl = redis.StrictRedis(host, port)
    name = register_engine(redis_cl, args["--name"], int(args["--workers"]))
    log("Starting daemon (Engine %s)..." % name)
    log("Waiting for jobs ...")
    run_interruptable(lambda: wait_jobs(redis_cl), "Shutting down ...")


if __name__ == '__main__':
    main()
