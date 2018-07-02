// Handler functions

{%- for device in graph_type['device_types'] %}

{%- set STATE_CLASS_NAME = device['id'] + "_state_t" -%}
{%- set PROP_CLASS_NAME = device['id'] + "_prop_t" -%}

    {% for pin in device['input_pins'] %}

    {%- set MSG_TYPE = pin['message_type'] + "_t" %}

    void receive_{{ MSG_TYPE }}(
    	{{- STATE_CLASS_NAME }}* deviceState,
    	{{- PROP_CLASS_NAME }}* deviceProperties,
    	{{- MSG_TYPE }} *message) {

        {{ pin['on_receive'] }}

    }
    {% endfor %}

{% endfor %}
