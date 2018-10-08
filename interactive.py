import json

from files import read_file
from files import read_json


user_functions = []  # list of functions to import into interpreter


def user_function(func):
    user_functions.append(func)
    return func


@user_function
def run(xml_file, region_map_file):
    """Run distributed simulation."""
    import redis
    redis_cl = redis.StrictRedis()
    xml = read_file(xml_file)
    region_map = read_json(region_map_file)
    job_queue = "cli1"
    job = {"xml": xml, "region_map": region_map, "result_queue": job_queue}
    job_str = json.dumps(job)
    redis_cl.delete(job_queue)
    redis_cl.rpush("jobs", job_str)
    result_str = redis_cl.blpop(job_queue)[1]
    result = json.loads(result_str)
    return result