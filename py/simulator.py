from __future__ import print_function

import os
import re
import sys
import random

from files import write_file
from pexpect import spawn
from datetime import datetime
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


def create_line_parser(states, metrics):

    def parse_field_str(field_str):
        fields = {}
        for item in field_str.split(', '):
            key, val = item.split(' = ')
            fields[key] = int(val)
        return fields

    def parse_state_line(device_name, field_str):
        states[device_name] = parse_field_str(field_str)

    def parse_metric_line(metric_name, value):
        if metric_name == "Delivered messages":
            old_count = metrics.get(metric_name, 0)
            metrics[metric_name] = old_count + int(value)
        else:
            metrics[metric_name] = int(value)

    preprocessors = [
        (r"^State \[(.+)\]: (.+)", parse_state_line),
        (r"^Metric \[(.+)\]: (.+)", parse_metric_line)
    ]

    pats = [re.compile(reg) for reg, _ in preprocessors]

    def parse_line(line):
        for pat, (_, line_parser) in zip(pats, preprocessors):
            for item in pat.findall(line):
                line_parser(*item)

    return parse_line


def simulate(schema, options):
    """Simulate a POETS schema.

    Arguments:
      - schema  (Schema) : POETS schema object
      - options (dict)   : Simulation parameters.

    Simulation parameters:
      - pid         (int)      : Process identifier
      - host        (str)      : Hostname of Redis instance
      - port        (int)      : Port of Redis instance
      - quiet       (bool)     : Suppress simulation output
      - debug       (bool)     : Print simulator debug information
      - level       (int)      : Log message verbosity level
      - region      (int)      : Simulation region
      - printer     (callable) : Print function for in-simulation outputs.
      - temp_dir    (str)      : Temp directory for simulation file
      - use_redis   (bool)     : Hook simulator to Redis via socat.

    Returns:
      - result      (dict) : Simulation results object
    """

    pid = options.get("pid", 0)
    host = options.get("host", "localhost")
    port = options.get("port", 6379)
    quiet = options.get("quiet", True)
    debug = options.get("debug", False)
    level = options.get("level", 1)
    region = options.get("region", 0)
    printer = options.get("printer", print)
    temp_dir = options.get("temp_dir", "/tmp")
    use_redis = options.get("use_redis", False)

    code = generate_code(schema, {"debug": debug, "level": level})
    engine_file = compile_gpp(code, temp_dir)

    # Define simulator invocation command.

    if use_redis:
        redis_con_str = "%s:%d" % (host, port)
        cmd_template = 'socat exec:"%s %d %d",fdout=3 tcp:' + redis_con_str
    else:
        cmd_template = "%s %d %d"

    cmd = cmd_template % (engine_file, region, pid)

    # Run simulation loop.

    states = {}
    metrics = {}
    parse_line = create_line_parser(states, metrics)

    engine = spawn(cmd, echo=False, timeout=None)

    while True:

        line = engine.readline().strip()

        if not line:
            break

        if not quiet:
            printer(line)

        parse_line(line)

    return {"states": states, "metrics": metrics}
