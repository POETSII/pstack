import json
import random
import beautifultable

from files import read_file
from files import read_json
from parser import parse_poets_xml
from schema import Schema

from simple_redis import redis_cl
from simple_redis import pop_json
from simple_redis import push_json


user_functions = []  # list of functions to import into interpreter


def user_function(func):
    user_functions.append(func)
    return func


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
def run(xml_file, region_map_file=None, name=None):
    """Run distributed POETS process."""
    name = name or "process-%s" % "".join(random.sample("0123456789", 6))
    result_queue = "cli1"
    xml = read_file(xml_file)
    region_map = read_json(region_map_file) if region_map_file else {}
    regions = Schema(parse_poets_xml(xml), region_map).get_regions()
    redis_cl.delete(result_queue)
    # Push simulation jobs to queue
    for region in regions:
        job = {
            "name": name,
            "xml": xml,
            "region": region,
            "region_map": region_map,
            "result_queue": result_queue
        }
        push_json(redis_cl, "jobs", job)
    # Collection simulation subresults
    subresults = [pop_json(redis_cl, result_queue) for _ in regions]
    # Combine into and return simulation result
    return combine_subresults(subresults)


def _format_table(table):
    """Style a beautifultable."""
    table.row_separator_char = ''
    table.intersection_char = ''
    table.left_border_char = ''
    table.right_border_char = ''
    left = beautifultable.BeautifulTable.ALIGN_LEFT
    for col_name in table.column_headers:
        table.column_alignments[col_name] = left


@user_function
def engines():
    """Print list of online POETS engines.

    Engine information are stored as JSON objects under client names as keys.
    """

    engines = [
        json.loads(redis_cl.get(client['name']))
        for client in redis_cl.client_list()
        if client['name']
    ]

    if not engines:
        print "No engines are currently connected"
        return

    def create_row(engine):
        name = engine['name'] or "unnamed"
        type_ = engine['type'] or "undeclared"
        reso = engine['resources'] or "undeclared"
        return [name, type_, reso]

    # Print engine information as a beautifultable
    table = beautifultable.BeautifulTable()
    table.column_headers = ["Engine", "Type", "Resources"]
    rows = map(create_row, engines)
    map(table.append_row, rows)
    _format_table(table)
    print(table)


@user_function
def pretty(obj):
    """Pretty-print JSON object."""
    print(json.dumps(obj, indent=4))