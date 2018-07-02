// Handler functions

{%- for device in graph_type['device_types'] %}

{%- set STATE_CLASS_NAME = device['id'] + "_state_t" -%}
{%- set PROP_CLASS_NAME = device['id'] + "_prop_t" -%}

    {% for pin in device['input_pins'] %}

    {%- set MSG_TYPE = pin['message_type'] + "_msg_t" %}

    void receive_{{ MSG_TYPE }}(state_t *state, prop_t *props, msg_t *msg) {
        {{ STATE_CLASS_NAME }}* deviceState = ({{ STATE_CLASS_NAME }}*) state;
        {{ PROP_CLASS_NAME }}* deviceProperties = ({{ PROP_CLASS_NAME}}*) props;
        {{ MSG_TYPE }} *message = ({{MSG_TYPE}}*) msg;
        {{ pin['on_receive'] }}

    }
    {% endfor %}

    int get_rts_{{ device['id']}}(state_t *state, prop_t *props) {
        int result;
        int* readyToSend = &result;
        {{ STATE_CLASS_NAME }}* deviceState = ({{ STATE_CLASS_NAME }}*) state;
        {{ PROP_CLASS_NAME }}* deviceProperties = ({{ PROP_CLASS_NAME}}*) props;
        {% for out_pin in device['output_pins'] %}
        {% set RTS_FLAG = 'RTS_FLAG_' + out_pin['message_type'] + '_out' %}
        const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
        {% endfor %}
        // Begin application code
        {{ device['ready_to_send'] }}
        // End application code
        return result;
    }

{% endfor %}
