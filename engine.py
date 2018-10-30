from datetime import datetime
from simple_redis import push_json


def clog(enabled, msg):
    """Print a log message, conditionally."""
    if enabled:
        now = datetime.utcnow()
        dt_str = now.strftime("%y-%m-%d %H:%M")
        print "%s - %s" % (dt_str, msg)


class Engine(object):

    def __init__(self, handler):
        self._initialized = False
        self.handler = handler
        self.verbose = False
        self.exit_code = None

    def setup(self, redis_cl, schema, pid, job, process):
        """Setup the engine."""
        self.pid = pid
        self.job = job
        self.process = process
        self.schema = schema
        self.device_list = get_device_list(schema)
        self.message_map = get_message_map(schema)
        self.incoming_edges = get_incoming_edges(schema, job["region"])
        self.outgoing_edges = get_outgoing_edges(schema, job["region"])
        self.redis_cl = redis_cl
        self.queue = "%d.%d" % (process["pid"], job["region"])
        self._initialized = True

    def _get_rcmd_shutdown(self, rcmd):
        """Process a remote command of type 'shutdown'."""
        self.exit_code = 0

        new_completed = self.redis_cl.incr(self.process["completed"])

        if new_completed == self.process["nregions"]:
            self.redis_cl.srem("running", pid)
            self.redis_cl.srem("pids", pid)

        dummy = {
            "log": [],
            "states": {},
            "metrics": {}
        }  # Returning results is not supported atm (TODO)

        push_json(self.redis_cl, self.process["result_queue"], dummy)

    def _get_rcmd_msg(self, rcmd):
        """Process a remote command of type 'message'."""

        # Unpack parts of remote command
        (device_ind, port, nfields), fields = rcmd[1:4], rcmd[4:]
        assert nfields == len(fields), "Message field count is incorrect"

        # Generate local messages
        for edge in self.incoming_edges:

            # edge: (src_dev, dst_dev, src_pin, dst_pin, dst_dev_region)

            if (edge[0], edge[2]) != (device_ind, port):
                continue

            src_device = self.device_list[edge[0]]
            dst_device = self.device_list[edge[1]]

            src_t = self.schema.get_device_type(src_device["type"])
            dst_t = self.schema.get_device_type(dst_device["type"])

            src_pin = src_t["output_pins"][edge[2]]
            dst_pin = dst_t["input_pins"][edge[3]]

            msg_t = self.message_map[dst_pin["message_type"]]
            scalars = msg_t["fields"]["scalars"]

            assert len(scalars) == len(fields), "Incorrect number of fields"

            payload = {
                scalar["name"]: value
                for scalar, value in zip(scalars, fields)
            }

            message = {
                "src": (src_device["id"], src_pin["name"]),
                "dst": (dst_device["id"], dst_pin["name"]),
                "type": msg_t["id"],
                "payload": payload
            }

            clog(self.verbose, "Received message: %s" % message)
            self.handler(self, message)

    def get(self):
        """Retrieve and process a remote command."""

        if not self._initialized:
            raise Exception("Engine is not initialized")

        rcmd_str = self.redis_cl.blpop(self.queue)[1]
        rcmd_int = [int(word) for word in rcmd_str.split()]
        rcmd_type = rcmd_int[0]  # remote command type

        if rcmd_type == 0:
            return self._get_rcmd_msg(rcmd_int)
        elif rcmd_type == 1:
            return self._get_rcmd_shutdown(rcmd_int)

        raise Exception("Received malformed remote command")

    def send(self, src, pin, **kwargs):
        src_dev = self.schema.get_device(src)
        src_dev_t = self.schema.get_device_type(src_dev["type"])
        src_pin = self.schema.get_pin(src_dev_t["id"], pin)
        msg_t = self.message_map[src_pin["message_type"]]
        fields = [
            kwargs.get(scalar["name"], 0)
            for scalar in msg_t["fields"]["scalars"]
        ]
        src_dev_ind = self.schema.get_device_index(src_dev["id"])
        src_pin_ind = self.schema.get_pin_index(src_dev_t["id"], pin, "output")
        rcmd = [0, src_dev_ind, src_pin_ind, len(fields)] + fields

        dst_regions = [
            item[4] for item in self.outgoing_edges
            if (item[0], item[2]) == (src_dev_ind, src_pin_ind)
        ]

        queues = ["%d.%d" % (self.pid, region) for region in dst_regions]
        rcmd_str = " ".join(map(str, rcmd))
        for queue in queues:
            self.redis_cl.rpush(queue, rcmd_str)

    def run(self, verbose=False):
        self.verbose = verbose
        clog(self.verbose, "Starting")
        while self.exit_code is None:
            self.get()
        clog(self.verbose, "Finished")





def get_device_list(schema):
    """Return list of schema devices."""
    def get_key(device):
        return (device["type"], device["id"])
    return sorted(schema.graph_inst["devices"], key=get_key)


def get_message_map(schema):
    """Return a map: msg id -> msg."""
    msg_types = schema.graph_type["message_types"]
    return {msg_tp["id"]: msg_tp for msg_tp in msg_types}


def get_incoming_edges(schema, region):
    """Return incoming subset of edge table.

    An edge table entry is "incoming" if the destination device is within the
    current simulation region.
    """
    return [item for item in schema.get_edge_table() if item[-1] == region]


def get_outgoing_edges(schema, region):
    """Return outgoing subset of edge table.

    An edge table entry is "outgoing" if the source device is within the current
    simulation region.
    """

    devices = schema.graph_inst["devices"]
    regions = schema.get_device_regions(devices)

    return [
        item for item in schema.get_edge_table()
        if regions[item[0]] == region
    ]
