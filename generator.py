import jinja2


def get_state_class(device_type):
    return "%s_state_t" % device_type


def get_props_class(device_type):
    return "%s_props_t" % device_type


def get_msg_class(message_type):
    return "%s_msg_t" % message_type


def get_device_class(device_type):
    return "%s_device_t" % device_type


def get_rts_flag_variable(output_pin):
    return "RTS_FLAG_%s" % (output_pin)


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
    """Return results of mapping funciton to items as a multi-line string."""

    return "\n".join(map(func, items))


def dict_from_list(list, field):
    """Create a dict from list using a specific field as key."""

    return {item[field]: item for item in list}


def unique(items):
    return list(set(items))


def pymap(func, items):
    return map(func, items)


def generate_code(template, content):
    """Generate code from template file and content dict."""

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
        get_receive_handler_name,
        get_send_handler_name,
        get_rts_getter_name,
        get_state_array,
        get_properties_array,
        build_index,
        get_init_function_name,
        get_device_array,
        declare_variable,
        make_argument_list,
        lmap,
        dict_from_list,
        unique,
        pymap
    ]

    for func in funcs:
        env.globals[func.func_name] = func

    return env.get_template(template).render(**content)
