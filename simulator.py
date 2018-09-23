import os
import re
import sys

from Queue import Queue
from struct import pack
from struct import unpack
from pexpect import spawn
from threading import Thread

def write_file(file, content):
    """Write string to file."""
    with open(file, 'w') as fid:
        fid.write(content)


def compile_gpp(code, temp_dir):
    """Compile C++ source file."""

    if not os.path.isdir(temp_dir):
         os.makedirs(temp_dir)

    source_file = os.path.join(temp_dir, 'psim.cpp')
    output_file = os.path.join(temp_dir, 'psim.exe')

    cmd = "g++ -fdiagnostics-color=always -o %s %s" % (output_file, source_file)

    write_file(source_file, code)
    exit_code = os.system(cmd)

    if exit_code is not 0:
        raise Exception("Compilation failed (%s)" % source_file)

    return output_file


def print_line(line):

    if line.startswith("msg: "):
        msg_bytes = line[5:]
        msg = unpack("<II", msg_bytes[:8])
        print "Got message, bytes =", list(bytearray(msg_bytes))
        print "Decoded message = %s" % repr(msg)

    else:
        print line

    sys.stdout.flush()


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


def run_worker(queue, index, cmd):
    """Run simulation worker."""

    engine = spawn(cmd, echo=False, timeout=None)

    while True:
        line = engine.readline()
        queue.put((index, line.strip()))
        if not line:
            break

    queue.put((index, None))


def simulate(code, quiet, temp_dir="/tmp"):
    """Run distributed simulation."""

    engine_file = compile_gpp(code, temp_dir)
    nworkers = 5

    cmd_sing = "%s %d"
    cmd_dist = 'socat exec:"%s %d",fdout=3 tcp:localhost:6379'
    cmd = cmd_dist if nworkers>1 else cmd_sing

    queue = Queue()

    def create_worker(index):
        args = (queue, index, cmd % (engine_file, index))
        return Thread(target=run_worker, args=args)

    workers = map(create_worker, range(nworkers))

    for worker in workers:
        worker.setDaemon(True)
        worker.start()

    log = []
    states = {}
    metrics = {}
    done = {index: False for index in range(nworkers)}

    parse_line = create_line_parser(log, states, metrics)

    while True:

        index, payload = queue.get()

        queue.task_done()

        if type(payload) is str:
            line = payload
            if not quiet:
                print "%s -> %s" % (index, line)
            parse_line(line.strip())
            continue

        done[index] = True

        if all(done.values()):
            break

    return {"log": log, "states": states, "metrics": metrics}
