// Device properties

{% for group in graph_instance['devices']|groupby('type') %}

{%- set device_type = group.grouper -%}
{%- set devices = group.list -%}
{%- set PROP_CLASS_NAME = device_type + "_prop_t" -%}
{%- set count = group.list|count -%}
{%- set PROP_ARR = "deviceProperties_" + device_type %}

{{PROP_CLASS_NAME}} {{ PROP_ARR }}[{{ count }}];

{% for device in devices -%}

{%- set properties = device['properties'] -%}

{%- set device_index = loop.index0 -%}

{%- for key, val in properties.iteritems() %}
	{{ PROP_ARR }}[{{ device_index }}].{{ key }} = {{ val }};
{%- endfor -%}

{%- endfor -%}

{%- endfor -%}
