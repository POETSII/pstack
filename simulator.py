import os
import sys

from struct import pack
from struct import unpack
from pexpect import spawn


def write_file(file, content):
    """Write string to file."""
    with open(file, 'w') as fid:
        fid.write(content)


def compile_gpp(code):
    """Compile C++ source file."""

    source_file, output_file = "tmp/psim.cpp", "tmp/psim.exe"
    cmd = "g++ -fdiagnostics-color=always -o %s %s" % (output_file, source_file)

    write_file(source_file, code)
    exit_code = os.system(cmd)

    if exit_code is not 0:
        raise Exception("Compilation failed (%s)" % source_file)

    return output_file


def simulate(code):

    engine_file = compile_gpp(code)
    engine = spawn(engine_file, echo=False, timeout=None)

    msg = pack("<IIII", 100, 1, 1, 5)
    sent = engine.send(msg + '\n')

    while True:

        response = engine.readline()

        if not response:
            return

        print response.strip()
        sys.stdout.flush()

        if response.startswith("msg: "):
            msg_bytes = response[5:]
            msg = unpack("<II", msg_bytes[:8])
            print "Got message, bytes =", list(bytearray(msg_bytes))
            print "Decoded message = %s" % repr(msg)
