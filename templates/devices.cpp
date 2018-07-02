// Device state types

class state_t {

    // Base device state type

};

class prop_t {

    // Base device properties type

};

{%- for device in graph_type['device_types'] %}

{% set STATE_CLASS_NAME = get_state_class(device['id']) %}

class {{ STATE_CLASS_NAME }}: public state_t {

public:

    {% for scalar in device['state']['scalars'] %}
    {{- scalar['type'] }} {{ scalar['name'] }};
    {% endfor %}

    {% for array in device['state']['arrays'] %}
    {{- array['type'] }} {{ array['name'] }}[{{ array['length'] }}];
    {% endfor %}

    {{ STATE_CLASS_NAME }} (){
    {%- for scalar in device['state']['scalars'] %}
        this->{{ scalar['name'] }} = 0;
    {%- endfor %}
    }

    void print() {
        {%- for scalar in device['state']['scalars'] %}
        printf("  - {{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
        {%- endfor %}
    }

};

{% endfor %}

// Device property types

{%- for device in graph_type['device_types'] %}

{% set PROP_CLASS_NAME = get_prop_class(device['id']) %}

class {{ PROP_CLASS_NAME }}: public prop_t {

public:

    {% for scalar in device['properties']['scalars'] %}
    {{- scalar['type'] }} {{ scalar['name'] }};
    {% endfor %}

};

{% endfor %}
