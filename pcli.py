#!/usr/bin/env python

import json
import redis

from files import read_file
from files import read_json


def run_job(redis_cl, xml, region_map):
    job_queue = "cli1"
    job = {"xml": xml, "region_map": region_map, "result_queue": job_queue}
    job_str = json.dumps(job)
    redis_cl.delete(job_queue)
    redis_cl.rpush("jobs", job_str)
    result_str = redis_cl.blpop(job_queue)[1]
    result = json.loads(result_str)
    return result


def main():
    redis_cl = redis.StrictRedis()
    xml = read_file("tests/ring-oscillator-01.xml")
    region_map = read_json("tmp/map1.json")
    result = run_job(redis_cl, xml, region_map)
    print json.dumps(result, indent=4)


if __name__ == '__main__':
    main()
