from pcli import ps
from pcli import run
from pcli import kill
from pcli import block
from pcli import Engine


"""Python Engines

An example of how to use the Engine class to hook Python functions into a
POETS process.

This example launches a ring oscillator process ('ring-oscillator-01.xml' from
the test directory), passing it an instance of pcli.Engine (my_engine) to
handle region 1 which contains the device "n1". my_engine then becomes
responsible for maintaining the state of this region (i.e. device "n1") by
processing incoming messages and generating outgoing ones. Since this is just
a ring oscillator, the handler function (receive) just forwards messages.

The Engine class showcased here permits powerful process manipulations with
three immediate capabilities in mind:

1. Input/Output: Use Python to implement various high-level interfaces (e.g.
REST, GRPC) to feed data in and out of a POETS process. For large quantities
of data, Python can invoke specialized high-performance serializers to
upload/download messages from Redis.

2. Instrumentation: Inspect application messages for profiling/debugging.

3. Development Productivitiy: Setup a basic XML template with device and
message types then prototype handlers in Python! This has the advantage of
making the entire Python ecosystem of tools and packages available for
developing applications for POETS. Once happy with the implementation,
translate to C.
"""


def receive(engine, msg):
    """React to a "Ring Oscillator" application message."""
    engine.send(src="n1", pin="toggle_out")


def main():

    # Create an engine that uses the handler
    my_engine = Engine(receive)

    # Start a process
    future = run(
        xml_file="tests/ring-oscillator-01.xml",
        rmap={"n1": 1},
        rcon={1: my_engine},
        async=True
    )

    # Run engine (in verbose mode to print details of what's happening)
    my_engine.run(verbose=True)

    # Collect and print process result
    print block(future)


if __name__ == '__main__':
    main()
