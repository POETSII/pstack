import os
import re
import sys
import random

from Queue import Queue
from files import write_file
from pexpect import spawn
from datetime import datetime
from threading import Thread
from generator import generate_code
from subprocess import call



def compile_gpp(code, temp_dir):
    """Compile C++ source file and return path to binary.."""

    datetime_str = datetime.utcnow().strftime(r"run-%Y%m%d-%H%M-")
    random_str = "".join(random.sample("0123456789", 6))

    subdirs = [temp_dir, "psim", datetime_str + random_str]
    sim_dir = os.path.join(*subdirs)

    source_file = os.path.join(sim_dir, 'psim.cpp')
    output_file = os.path.join(sim_dir, 'psim.exe')

    flags = "-std=c++11 -fdiagnostics-color=always"
    gpp_cmd = "g++ %s -o %s %s" % (flags, output_file, source_file)

    # Create simulation directory (plus parents, if necessary).
    if not os.path.isdir(sim_dir):
         os.makedirs(sim_dir)

    # Write source file and compile.
    write_file(source_file, code)
    exit_code = call(gpp_cmd, shell=True)

    if exit_code != 0:
        raise Exception("Compilation failed (%s)" % source_file)

    # Return path to compiled binary.
    return output_file


def create_line_parser(log, states, metrics):

    def parse_field_str(field_str):
        fields = {}
        for item in field_str.split(', '):
            key, val = item.split(' = ')
            fields[key] = int(val)
        return fields

    def parse_app_line(device_name, log_level, msg):
        entry = device_name, int(log_level), msg
        log.append(entry)

    def parse_state_line(device_name, field_str):
        states[device_name] = parse_field_str(field_str)

    def parse_metric_line(metric_name, value):
        if metric_name == "Delivered messages":
            old_count = metrics.get(metric_name, 0)
            metrics[metric_name] = old_count + int(value)
        else:
            metrics[metric_name] = int(value)

    preprocessors = [
        (r"^App \[(.+), (\d+)]: (.+)", parse_app_line),
        (r"^State \[(.+)\]: (.+)", parse_state_line),
        (r"^Metric \[(.+)\]: (.+)", parse_metric_line)
    ]

    pats = [re.compile(reg) for reg, _ in preprocessors]

    def parse_line(line):
        for pat, (_, line_parser) in zip(pats, preprocessors):
            for item in pat.findall(line):
                line_parser(*item)

    return parse_line


def run_worker(queue, region, cmd):
    """Run simulation worker."""

    engine = spawn(cmd, echo=False, timeout=None)

    while True:
        line = engine.readline()
        queue.put((region, line.strip()))
        if not line:
            break

    queue.put((region, None))


def simulate(schema, options):
    """Simulate a POETS schema.

    Arguments:
      - schema  (Schema) : POETS schema object
      - options (dict)   : Simulation parameters.

    Simulation parameters:
      - quiet       (bool) : Suppress simulation output
      - debug       (bool) : Print simulator debug information
      - level       (int)  : Log message verbosity level
      - redis       (str)  : Hostname and port of Redis instance
      - regions     (list) : List of regions to simulate
      - temp_dir    (str)  : Temp directory for simulation file
      - force_socat (bool) : Force using socat (single-region simulations)

    Returns:
      - result      (dict) : Simulation results object
    """

    host = options.get("host", "localhost")
    port = options.get("port", 6379)
    quiet = options.get("quiet", False)
    debug = options.get("debug", False)
    level = options.get("level", 1)
    regions = options.get("regions", schema.get_regions())
    temp_dir = options.get("temp_dir", "/tmp")
    force_socat = options.get("force_socat", False)

    code = generate_code(schema, {"debug": debug, "level": level})
    engine_file = compile_gpp(code, temp_dir)
    regions = regions or schema.get_regions()

    # Define simulator invokation command.
    if len(regions)>1 or force_socat:
        redis_connection_str = "%s:%d" % (host, port)
        cmd = 'socat exec:"%s %d",fdout=3 tcp:' + redis_connection_str
    else:
        cmd = "%s %d"

    queue = Queue()

    def create_worker(region):
        args = (queue, region, cmd % (engine_file, region))
        return Thread(target=run_worker, args=args)

    workers = map(create_worker, regions)

    for worker in workers:
        worker.setDaemon(True)
        worker.start()

    log = []
    states = {}
    metrics = {}
    done = {region: False for region in regions}

    parse_line = create_line_parser(log, states, metrics)

    while True:

        region, payload = queue.get()

        queue.task_done()

        if type(payload) is str:
            line = payload
            if not quiet:
                print "%s -> %s" % (region, line)
            parse_line(line.strip())
            continue

        done[region] = True

        if all(done.values()):
            break

    return {"log": log, "states": states, "metrics": metrics}
