from parser import parse_poets_xml


def _build_pin_map(graph_type):
    """Build a map: (device id, pin_name) -> pin."""

    result = dict()

    for device in graph_type["device_types"]:
        for pin in device['input_pins'] + device['output_pins']:
            key = (device['id'], pin['name'])
            result[key] = pin

    return result


def _build_device_type_map(graph_type):
    """Build a map: device id -> device."""

    return {device["id"]: device for device in graph_type["device_types"]}


def _build_pin_index(graph_type, pin_dir):
    """Build a map: (device id, pin name) -> index for input/output pins."""

    result = dict()
    pins_key = 'input_pins' if pin_dir == 'input' else 'output_pins'

    for device in graph_type["device_types"]:
        entries = {
            (device['id'], pin['name']): ind
            for ind, pin in enumerate(device[pins_key])
        }
        result.update(entries)

    return result


def _build_device_index(graph_inst):
    """Build a map: device id -> index."""

    def get_key(device):
        return (device['type'], device['id'])

    devices_sorted = sorted(graph_inst['devices'], key=get_key)
    return {device['id']: index for index, device in enumerate(devices_sorted)}


def _build_device_map(graph_inst):

    return {device['id']: device for device in graph_inst['devices']}


class Schema(object):

    def __init__(self, xml, region_map={}):
        self.graph_type, self.graph_inst = parse_poets_xml(xml)
        self._region_map = region_map
        self._pin_map = _build_pin_map(self.graph_type)
        self._device_map = _build_device_map(self.graph_inst)
        self._device_index = _build_device_index(self.graph_inst)
        self._device_type_map = _build_device_type_map(self.graph_type)
        self._input_pin_index = _build_pin_index(self.graph_type, 'input')
        self._output_pin_index = _build_pin_index(self.graph_type, 'output')

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

            dst_dev_region = self._region_map.get(dst_device, 0)

            return (src_device_index, dst_device_index, src_pin, dst_pin, dst_dev_region)

        edges = self.graph_inst["edges"]

        return map(get_table_entry, edges)

    def get_regions(self):
        """Return list of simulation regions.

        Regions are the (unique) values in _region_map, plus 0 (the default
        region) if there are any devices with no matching entries in
        _region_map.
        """

        devices = self.graph_inst['devices']
        all_regions = [self._region_map.get(dev["id"], 0) for dev in devices]
        return list(set(all_regions))

    def get_device_regions(self, devices):
        """Return list of regions corresponding to list of devices.

        Assumes a default region of 0.
        """
        return [self._region_map.get(dev["id"], 0) for dev in devices]
