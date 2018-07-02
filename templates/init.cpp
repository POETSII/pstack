{% for group in graph_instance['devices']|groupby('type') %}

{%- set device_type = group.grouper -%}
{%- set devices = group.list -%}
{%- set STATE_CLASS_NAME = device_type + "_state_t" -%}
{%- set PROP_CLASS_NAME = device_type + "_prop_t" -%}
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

__init___msg_t *init = new __init___msg_t();

for (int i=0; i<{{ count}}; i++)
	receive___init___msg_t({{ STAT_ARR }} + i, {{ PROP_ARR }} + i, init);

{%- endfor -%}
