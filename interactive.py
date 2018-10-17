import json
import redis
import random
import beautifultable

from files import read_file
from files import read_json
from parser import parse_poets_xml

from simple_redis import pop_json
from simple_redis import push_json


redis_cl = redis.StrictRedis()
user_functions = []  # list of functions to import into interpreter


def user_function(func):
    user_functions.append(func)
    return func


@user_function
def help():
    """Show available functions."""
    header = ["Function", "Description"]
    def key(func):
        return (len(func.__name__), len(func.__doc__))
    body = [
        (func.__name__, func.__doc__ or "(unavailable)")
        for func in sorted(user_functions, key=key)
    ]
    table = [header] + body
    pp_table(table)


@user_function
def read(file):
    """Read file."""
    return read_file(file)


@user_function
def instance(xml_file):
    """Show graph instance information of an XML file."""
    xml = read_file(xml_file)
    instance = parse_poets_xml(xml)[1]
    result = {"devices": len(instance["devices"]),
              "edges": len(instance["edges"])}
    pretty(result)


@user_function
def messages(xml_file):
    """Show message type information of an XML file."""
    xml = read_file(xml_file)
    gtype = parse_poets_xml(xml)[0]
    messages = {msg["id"]: msg for msg in gtype["message_types"]}
    pretty(messages)


@user_function
def devices(xml_file):
    """Show device type information of an XML file."""
    attr = lambda atribute, items: [item[atribute] for item in items]
    xml = read_file(xml_file)
    graph_type = parse_poets_xml(xml)[0]
    devices = {
        dev["id"]: {
            "state": {
                "scalars": attr("name", dev["state"].get("scalars", [])),
                "arrays": attr("name", dev["state"].get("arrays", []))
            },
            "pins": {
                "input": attr("name", dev["input_pins"]),
                "output": attr("name", dev["output_pins"])
            }
        }
        for dev in graph_type["device_types"]
    }
    pretty(devices)


def combine_subresults(subresults):
    """Combine the subresults of region simulations."""

    def merge_dicts(dicts):
        """Merge dictionaries into one."""
        result = {}
        for item in dicts:
            result.update(item)
        return result

    def sum_dict_fields(dicts):
        """Sum the fields of several dictionaries."""
        result = {}
        for item in dicts:
            for key, val in item.iteritems():
                result[key] = result.get(key, 0) + val
        return result

    def flatten(lists):
        """Flatten list of lists."""
        return sum(lists, [])

    return {
        "logs": flatten(sub["log"] for sub in subresults),
        "states": merge_dicts(sub["states"] for sub in subresults),
        "metrics": sum_dict_fields(sub["metrics"] for sub in subresults)
    }


@user_function
def run(xml_file, region_map_file=None, name=None, verbose=False):
    """Start a POETS process."""
    name = name or "process-%s" % "".join(random.sample("0123456789", 6))
    result_queue = "result-%s" % "".join(random.sample("0123456789", 6))
    xml = read_file(xml_file)
    region_map = read_json(region_map_file) if region_map_file else {}
    regions = Schema(xml, region_map).get_regions()
    redis_cl.delete(result_queue)
    # Push simulation jobs to queue
    for region in regions:
        job = {
            "name": name,
            "xml": xml,
            "region": region,
            "verbose": verbose,
            "region_map": region_map,
            "result_queue": result_queue
        }
        push_json(redis_cl, "jobs", job)
    # Collection simulation log messages and results
    subresults = []
    while len(subresults) < len(regions):
        item = pop_json(redis_cl, result_queue)
        if type(item) in {str, unicode}:
            print "-> %s" % item
        else:
            subresults.append(item)
    # Combine into and return simulation result
    return combine_subresults(subresults)


def pp_table(table):
    """Pretty print a table.

    Arguments:
      - table (list) : list of rows, each a list of str.

    First row is taken as a header and remaining row as table body.
    """

    btable = beautifultable.BeautifulTable()
    btable.column_headers = table[0]
    btable.row_separator_char = ''
    btable.intersection_char = ''
    btable.left_border_char = ''
    btable.right_border_char = ''
    left = beautifultable.BeautifulTable.ALIGN_LEFT
    for column in btable.column_headers:
        btable.column_alignments[column] = left
    map(btable.append_row, table[1:])
    print(btable)


@user_function
def engines():
    """Print list of online POETS engines."""

    engines = [
        json.loads(redis_cl.get(client['name']))
        for client in redis_cl.client_list()
        if client['name']
    ]

    def sort_engines(engine):
        """Sort key function.

        Sorts engines by number of workers (desc) then engine name (asc).
        """
        nworkers = int(engine.get("_nresources", 0))
        name = engine['name']
        return (-nworkers, name)

    if not engines:
        print "No engines are currently connected"
        return

    def create_row(engine):
        name = engine.get("name", "unnamed")
        type_ = engine.get("type", "undeclared")
        reso = engine.get("resources", "undeclared")
        usage = engine.get("usage", "unknown")
        return [name, type_, reso, usage]

    # Print engine information as a beautifultable
    body = map(create_row, sorted(engines, key=sort_engines))
    header = ["Engine", "Type", "Resources", "Usage"]
    table = [header] + map(create_row, engines)
    pp_table(table)


@user_function
def pretty(obj):
    """Pretty-print JSON object."""
    print(json.dumps(obj, indent=4))
