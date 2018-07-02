{% for group in graph_instance['devices']|groupby('type') %}

{%- set device_type = group.grouper -%}
{%- set devices = group.list -%}
{%- set STATE_CLASS_NAME = get_state_class(device_type) -%}
{%- set PROP_CLASS_NAME = get_prop_class(device_type) -%}
{%- set count = group.list|count -%}
{%- set PROP_ARR = "deviceProperties_" + device_type %}
{%- set STAT_ARR = "deviceStates_" + device_type %}

	// States of {{ device_type }}

{{ STATE_CLASS_NAME }} {{ STAT_ARR }}[{{ count }}];

	// Properties of {{ device_type }}

{{PROP_CLASS_NAME}} {{ PROP_ARR }}[{{ count }}];

{% for device in devices -%}

{%- set properties = device['properties'] -%}

{%- set device_index = loop.index0 -%}

{%- for key, val in properties.iteritems() %}
	{{ PROP_ARR }}[{{ device_index }}].{{ key }} = {{ val }};
{%- endfor -%}

{%- endfor %}

	// Call initialization handler

{% set INIT_MSG_T = get_msg_class('__init__') %}
{% set INIT_HANDLER = get_receive_handler_name(device_type, '__init__') %}

{{ INIT_MSG_T }} *init = new {{ INIT_MSG_T }}();

for (int i=0; i<{{ count}}; i++)
	{{ INIT_HANDLER}}({{ STAT_ARR }} + i, {{ PROP_ARR }} + i, init);

{%- endfor -%}
