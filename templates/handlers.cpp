// Handler functions

{%- for device in graph_type['device_types'] %}

{%- set STATE_CLASS_NAME = device['id'] + "_state_t" -%}
{%- set PROP_CLASS_NAME = device['id'] + "_prop_t" -%}

    {% for pin in device['input_pins'] %}

    {%- set MSG_TYPE = pin['message_type'] + "_t" %}

    void receive_{{ MSG_TYPE }}(
        {{ STATE_CLASS_NAME }}* deviceState,
        {{ PROP_CLASS_NAME }}* deviceProperties,
        {{ MSG_TYPE }} *message) {

        {{ pin['on_receive'] }}

    }
    {% endfor %}

    int get_rts_{{ device['id']}}(
        {{ STATE_CLASS_NAME }}* deviceState,
        {{ PROP_CLASS_NAME }}* deviceProperties) {
        int result;
        int* readyToSend = &result;
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
