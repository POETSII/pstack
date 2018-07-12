import jinja2

from itertools import groupby


class Schema(object):

    def __init__(self, markup):
        self._pin_map = self._build_pin_map(markup)
        self._device_map = self._build_device_map(markup)
        self._device_type_map = self._build_device_type_map(markup)
        self._input_pin_index = self._build_pin_index(markup, 'input')
        self._output_pin_index = self._build_pin_index(markup, 'output')
        self._device_index = self._build_device_index(markup)
        self._edge_table = self._build_edge_table(markup)

    def _build_pin_map(self, markup):
        """Build a map: (device id, pin_name) -> pin."""

        result = dict()

        graph_type = markup["graph_type"]

        for device in graph_type["device_types"]:
            for pin in device['input_pins'] + device['output_pins']:
                key = (device['id'], pin['name'])
                result[key] = pin

        return result

    def _build_device_type_map(self, markup):
        """Build a map: device id -> device."""

        device_types = markup["graph_type"]["device_types"]
        result = {device["id"]: device for device in device_types}
        return result

    def _build_pin_index(self, markup, pin_dir):
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

    def _build_device_index(self, markup):
        """Build a map: device id -> index."""

        devices = markup['graph_instance']['devices']

        def get_key(device):
            return (device['type'], device['id'])

        devices_sorted = sorted(devices, key=get_key)

        return {device['id']: index for index, device in enumerate(devices_sorted)}


    def _build_device_map(self, markup):

        devices = markup['graph_instance']['devices']

        return {device['id']: device for device in devices}

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

    def _build_edge_table(self, markup):

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

        edges = markup["graph_instance"]["edges"]

        return map(get_table_entry, edges)

    def get_edge_table(self):

        return self._edge_table


def get_state_class(device_type):
    return "%s_state_t" % device_type


def get_props_class(device_type):
    return "%s_props_t" % device_type


def get_msg_class(message_type):
    return "%s_msg_t" % message_type


def get_device_class(device_type):
    return "%s_device_t" % device_type


def get_graph_type_props_class(graph_type_id):
    return "%s_properties_t" % graph_type_id


def get_rts_flag_variable(output_pin):
    return "RTS_FLAG_%s" % (output_pin)


def get_rts_flag_obsolete_variable(device_type, output_pin):
    return "RTS_FLAG_%s_%s" % (device_type, output_pin)


def get_receive_handler_name(device_type, message_type):
    return "_receive_%s_%s" % (device_type, message_type)


def get_send_handler_name(device_type, message_type):
    return "_send_%s_%s" % (device_type, message_type)


def get_rts_getter_name(device_type):
    return "_get_rts_%s" % device_type


def get_state_array(device_type):
    return "deviceStates_%s" % device_type


def get_properties_array(device_type):
    return "deviceProperties_%s" % device_type


def get_device_array(device_type):
    return "devices_%s" % device_type


def get_init_function_name(device_type):
    return "initialize_%s_devices" % device_type


def declare_variable(variable):
    """Create C variable declaration.

    Examples:
        int a;
        int b[100];

    `variable` can be a scalar or an array object.
    """

    if "length" in variable:
        array_bracket = "[%d]" % variable["length"]
    else:
        array_bracket = ""

    return "%s %s %s;" % (variable["type"], variable["name"], array_bracket)


def make_argument_list(variables, include_types=True):
    """Create C argument list.

    Example: "int a, int b, float c"

    if include_types is False then types are ommitted

    """

    format_str = "%(type)s %(name)s" if include_types else "%(name)s"

    parts = [format_str % var for var in variables]

    return ", ".join(parts)


def build_index(items):
    unique_items = list(set(items))
    return {item: index for index, item in enumerate(sorted(unique_items))}


def lmap(func, items):
    """Return results of mapping function to items as a multi-line string."""

    return "\n".join(map(func, items))


def unique(items):
    return list(set(items))


def pymap(func, items):
    return map(func, items)


def mformat(fmt_str, items):
    return [fmt_str % item for item in items]


def generate_code(template, graph):
    """Generate code from template file and POETS graph."""

    loader = jinja2.PackageLoader(__name__, 'templates')
    env = jinja2.Environment(loader=loader)
    env.line_statement_prefix = '@'

    # Add functions to Jinja context
    funcs = [
        get_state_class,
        get_props_class,
        get_msg_class,
        get_device_class,
        get_rts_flag_variable,
        get_rts_flag_obsolete_variable,
        get_receive_handler_name,
        get_send_handler_name,
        get_rts_getter_name,
        get_state_array,
        get_properties_array,
        get_graph_type_props_class,
        build_index,
        get_init_function_name,
        get_device_array,
        declare_variable,
        make_argument_list,
        lmap,
        unique,
        pymap,
        mformat
    ]

    for func in funcs:
        env.globals[func.func_name] = func

    env.globals["schema"] = Schema(graph)

    return env.get_template(template).render(**graph)
