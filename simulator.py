import os
import re
import sys

from struct import pack
from struct import unpack
from pexpect import spawn


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


def simulate(code, temp_dir="/tmp"):

    engine_file = compile_gpp(code, temp_dir)
    engine = spawn(engine_file, echo=False, timeout=None)

    msg = pack("<IIII", 100, 1, 1, 5)
    sent = engine.send(msg + '\n')

    log = []
    states = {}
    metrics = {}

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

    while True:

        line = engine.readline()

        if not line:
            break

        print_line(line.strip())
        parse_line(line.strip())

    return {"log": log, "states": states, "metrics": metrics}
