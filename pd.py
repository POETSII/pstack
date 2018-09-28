import json
import psim
import redis
import docopt


usage="""POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of POETS workers [default: 2].
  -r --redis=<host>  Specify Redis host [default: localhost:6379].
  -q --quiet         Suppress all outputs.

"""


def _psim(xml, region_map):
    """Run PSIM simulation."""
    options = {"debug": False, "level": 0}
    markup = psim.parse_poets_xml(xml)
    code, nregions = psim.generate_code(markup, options, region_map)
    result = psim.simulate(code, quiet=True, nworkers=nregions)
    return result


def fetch_job(redis_cl):
    """Retrieve job from Redis "jobs" queue."""
    json_str = redis_cl.blpop("jobs")[1]
    job = json.loads(json_str)
    return job


def parse_connection_str(con_str):
    """Parse connection string in the form host:port."""
    try:
        host_str, port_str = con_str.split(':')
        return (host_str, int(port_str))
    except ValueError:
        raise Exception("Could not parse '%s'" % con_str)


def wait_jobs(redis_cl):
    """Wait for and process jobs from Redis "jobs" queue."""
    while True:
        job = fetch_job(redis_cl)
        print "Received job"
        result = _psim(job["xml"], job["region_map"])
        result_str = json.dumps(result, indent=4)
        redis_cl.rpush(job["result_queue"], result_str)


def main():
    args = docopt.docopt(usage, version="v0.1")
    host, port = parse_connection_str(args["--redis"])
    redis_cl = redis.StrictRedis(host, port)
    print "Waiting for jobs ..."
    wait_jobs(redis_cl)


if __name__ == '__main__':
    main()
