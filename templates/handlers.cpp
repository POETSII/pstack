// Handler functions

{%- for device_type in graph_type['device_types'] %}

{%- set STATE_CLASS_NAME = get_state_class(device_type['id']) -%}
{%- set PROP_CLASS_NAME = get_prop_class(device_type['id']) -%}

    {% for pin in device_type['input_pins'] %}

    {%- set MSG_TYPE = get_msg_class(pin['message_type']) %}
    {%- set HANDLER_NAME = get_receive_handler_name(device_type['id'], pin['message_type']) %}

    void {{ HANDLER_NAME }}(state_t *state, prop_t *props, msg_t *msg) {
        {{ STATE_CLASS_NAME }}* deviceState = ({{ STATE_CLASS_NAME }}*) state;
        {{ PROP_CLASS_NAME }}* deviceProperties = ({{ PROP_CLASS_NAME}}*) props;
        {{ MSG_TYPE }} *message = ({{MSG_TYPE}}*) msg;
        {{ pin['on_receive'] }}

    }
    {% endfor %}

    int get_rts_{{ device_type['id']}}(state_t *state, prop_t *props) {
        int result;
        int* readyToSend = &result;
        {{ STATE_CLASS_NAME }}* deviceState = ({{ STATE_CLASS_NAME }}*) state;
        {{ PROP_CLASS_NAME }}* deviceProperties = ({{ PROP_CLASS_NAME}}*) props;
        {% for out_pin in device_type['output_pins'] %}
        {% set RTS_FLAG = get_rts_flag_variable(out_pin['message_type']) %}
        const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
        {% endfor %}
        // Begin application code
        {{ device_type['ready_to_send'] }}
        // End application code
        return result;
    }

{% endfor %}
