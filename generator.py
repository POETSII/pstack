import jinja2


def get_state_class(device_type):
    return "%s_state_t" % device_type


def get_prop_class(device_type):
    return "%s_props_t" % device_type


def get_msg_class(message_type):
    return "%s_msg_t" % message_type


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


def get_init_function_name(device_type):
    return "initialize_%s_devices" % device_type


def build_index(items):
    unique_items = list(set(items))
    return {item: index for index, item in enumerate(sorted(unique_items))}


def generate_code(template, content):
    """Generate code from template file and content dict."""

    loader = jinja2.PackageLoader(__name__, 'templates')
    env = jinja2.Environment(loader=loader)
    env.line_statement_prefix = '@'

    # Add functions to Jinja context
    funcs = [
        get_state_class,
        get_prop_class,
        get_msg_class,
        get_rts_flag_variable,
        get_receive_handler_name,
        get_send_handler_name,
        get_rts_getter_name,
        get_state_array,
        get_properties_array,
        build_index,
        get_init_function_name
    ]

    for func in funcs:
        env.globals[func.func_name] = func

    return env.get_template(template).render(**content)
