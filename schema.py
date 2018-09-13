def _build_pin_map(markup):
    """Build a map: (device id, pin_name) -> pin."""

    result = dict()

    graph_type = markup["graph_type"]

    for device in graph_type["device_types"]:
        for pin in device['input_pins'] + device['output_pins']:
            key = (device['id'], pin['name'])
            result[key] = pin

    return result


def _build_device_type_map(markup):
    """Build a map: device id -> device."""

    device_types = markup["graph_type"]["device_types"]
    result = {device["id"]: device for device in device_types}
    return result


def _build_pin_index(markup, pin_dir):
    """Build a map: (device id, pin name) -> index for input/output pins."""

    result = dict()
    pins_key = 'input_pins' if pin_dir == 'input' else 'output_pins'
    graph_type = markup["graph_type"]

    for device in graph_type["device_types"]:
        entries = {
            (device['id'], pin['name']): ind
            for ind, pin in enumerate(device[pins_key])
        }
        result.update(entries)

    return result


def _build_device_index(markup):
    """Build a map: device id -> index."""

    devices = markup['graph_instance']['devices']

    def get_key(device):
        return (device['type'], device['id'])

    devices_sorted = sorted(devices, key=get_key)

    return {device['id']: index for index, device in enumerate(devices_sorted)}


def _build_device_map(markup):

    devices = markup['graph_instance']['devices']

    return {device['id']: device for device in devices}


class Schema(object):

    def __init__(self, markup, region_map):
        self._markup = markup
        self._region_map = region_map
        self._pin_map = _build_pin_map(markup)
        self._device_map = _build_device_map(markup)
        self._device_index = _build_device_index(markup)
        self._device_type_map = _build_device_type_map(markup)
        self._input_pin_index = _build_pin_index(markup, 'input')
        self._output_pin_index = _build_pin_index(markup, 'output')

    def get_pin(self, device_type, pin_name):
        """Return pin given device and pin names."""

        key = (device_type, pin_name)
        return self._pin_map.get(key)

    def get_pin_index(self, device_type, pin_name, pin_dir):
        """Return pin index.

        The index is unique per device type and pin direction.
        """

        assert pin_dir in {'input', 'output'}

        if pin_dir == 'input':
            index = self._input_pin_index
        else:
            index = self._output_pin_index

        return index[(device_type, pin_name)]

    def get_device_type(self, device_id):
        """Return device type."""
        return self._device_type_map.get(device_id)

    def get_device_index(self, device_id):
        """Return device index (unique per device type)."""
        return self._device_index[device_id]

    def get_device(self, device_id):
        return self._device_map[device_id]

    def get_edge_table(self):

        def get_table_entry(edge):

            src_device, src_pin_name = edge['src']
            dst_device, dst_pin_name = edge['dst']

            src_device_index = self.get_device_index(src_device)
            dst_device_index = self.get_device_index(dst_device)

            src_device_type = self.get_device(src_device)['type']
            dst_device_type = self.get_device(dst_device)['type']

            src_pin = self.get_pin_index(src_device_type, src_pin_name, 'output')
            dst_pin = self.get_pin_index(dst_device_type, dst_pin_name, 'input')

            return (src_device_index, dst_device_index, src_pin, dst_pin)

        edges = self._markup["graph_instance"]["edges"]

        return map(get_table_entry, edges)

    def get_region_count(self):
        return len({region for region in self._region_map.values()})

    def get_device_regions(self, devices):
        """Return list of regions corresponding to list of devices.

        Assumes a default region of 0.
        """
        return [self._region_map.get(dev["id"], 0) for dev in devices]
