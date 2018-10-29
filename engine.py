class Engine(object):

    def __init__(self):
        self._initialized = False

    def setup(self, redis_cl, schema, pid, region):
        """Setup the engine."""
        self.pid = pid
        self.region = region
        self.schema = schema
        self.device_list = get_device_list(schema)
        self.message_map = get_message_map(schema)
        self.local_edge_table = get_local_edge_table(schema, region)
        self.redis_cl = redis_cl
        self.queue = "%d.%d" % (pid, region)
        self.get_handlers = {
            0: self._get_rcmd_msg,
            1: self._get_rcmd_shutdown
        }
        self._initialized = True

    def _get_rcmd_shutdown(self, rcm):
        """Process a remote command of type 'shutdown'."""
        assert rcm[0] == 1, "Remote command is not of 'shutdown' type"
        return "<shutdown>"

    def _get_rcmd_msg(self, rcmd):
        """Process a remote command of type 'message'."""

        assert rcmd[0] == 0, "Remote command is not of 'message' type"

        # Unpack parts of remote command
        header, fields = rcmd[1:4], rcmd[4:]
        device_ind, port, nfields = header

        assert nfields == len(fields), "Message field count is incorrect"

        messages = []  # list of local messages to generate

        for src_dev, dst_dev, src_pin, dst_pin, _ in self.local_edge_table:

            if (src_dev, src_pin) != (device_ind, port):
                continue

            device = self.device_list[dst_dev]
            dev_type_id = device["type"]
            dev_type = self.schema.get_device_type(dev_type_id)
            dst_pin = dev_type["input_pins"][dst_pin]
            msg_type_id = dst_pin["message_type"]
            msg_type = self.message_map[msg_type_id]
            scalars = msg_type["fields"]["scalars"]

            assert len(scalars) == len(fields), "Incorrect number of fields"

            payload = {
                scalar["name"]: value
                for scalar, value in zip(scalars, fields)
            }

            message = {
                "to": (device["id"], dst_pin["name"]),
                "type": msg_type_id,
                "payload": payload
            }

            messages.append(message)

        return messages

    def _get_rcmd_unknown(self, _):
        raise Exception("Received malformed remote command")

    def get(self, async=False):
        if not self._initialized:
            raise Exception("Engine is not initialized")
        _, rcmd_str = self.redis_cl.blpop(self.queue)
        rcmd = [int(word) for word in rcmd_str.split()]
        rcmd_type = rcmd[0]  # remote command type
        handler = self.get_handlers.get(rcmd_type, self._get_rcmd_unknown)
        return handler(rcmd)


def get_device_list(schema):
    """Return list of schema devices."""
    def get_key(device):
        return (device["type"], device["id"])
    return sorted(schema.graph_inst["devices"], key=get_key)


def get_message_map(schema):
    """Return a map: msg id -> msg."""
    msg_types = schema.graph_type["message_types"]
    return {msg_tp["id"]: msg_tp for msg_tp in msg_types}


def get_local_edge_table(schema, region):
    """Return local subset of edge table.

    An edge table entry is "local" if the destination device is within the
    current simulation region.
    """
    return [item for item in schema.get_edge_table() if item[-1] == region]

