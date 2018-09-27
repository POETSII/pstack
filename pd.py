import json
import docopt
import redis


usage="""POETS Daemon (PD) v0.1

Usage:
  pd.py [options]

Options:
  -w --workers=<n>   Specify number of POETS workers [default: 2].
  -r --redis=<host>  Specify Redis host [default: localhost:6379].
  -q --quiet         Suppress all outputs.

"""


def fetch_job(redis_cl):
    json_str = redis_cl.blpop("jobs")[1]
    job = json.loads(json_str)
    return job


def parse_connection_str(con_str):
    try:
        host_str, port_str = con_str.split(':')
        return (host_str, int(port_str))
    except ValueError:
        raise Exception("Could not parse '%s'" % con_str)


def wait_jobs(redis_cl):
    while True:
        job = fetch_job(redis_cl)
        print "Received job:", job


def main():
    args = docopt.docopt(usage, version="v0.1")
    host, port = parse_connection_str(args["--redis"])
    redis_cl = redis.StrictRedis(host, port)
    print "Waiting for jobs ..."
    wait_jobs(redis_cl)


if __name__ == '__main__':
    main()
