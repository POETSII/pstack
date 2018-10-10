import json
import redis
import beautifultable

from files import read_file
from files import read_json

user_functions = []  # list of functions to import into interpreter

redis_cl = redis.StrictRedis()  # Redis client


def user_function(func):
    user_functions.append(func)
    return func


def push_json(queue, obj):
    """Push JSON object to Redis queue."""
    obj_json = json.dumps(obj)
    redis_cl.rpush(queue, obj_json)


def pop_json(queue):
    """Pop JSON object from Redis queue."""
    obj_str = redis_cl.blpop(queue)[1]
    return json.loads(obj_str)


@user_function
def run(xml_file, region_map_file):
    """Run distributed simulation."""
    xml = read_file(xml_file)
    region_map = read_json(region_map_file)
    result_queue = "cli1"
    job = {"xml": xml, "region_map": region_map, "result_queue": result_queue}
    redis_cl.delete(result_queue)
    push_json("jobs", job)
    return pop_json(result_queue)


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
