// Device types

{%- for device in graph_type['device_types'] %}
{% set CLASS_NAME = device['id'] + "_state_t" %}
class {{ CLASS_NAME }} {

public:

    {% for scalar in device['state']['scalars'] %}
    {{- scalar['type'] }} {{ scalar['name'] }};
    {% endfor %}

    {% for array in device['state']['arrays'] %}
    {{- array['type'] }} {{ array['name'] }}[{{ array['length'] }}];
    {% endfor %}

    {{ CLASS_NAME }} (){
    {%- for scalar in device['state']['scalars'] %}
        this->{{ scalar['name'] }} = 0;
    {%- endfor %}
    }

    void print() {
        {%- for scalar in device['state']['scalars'] %}
        printf("{{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
        {%- endfor %}
    }

{#
    {% for pin in device['input_pins'] %}
    {%- set MSG_TYPE = pin['message_type'] + "_t" %}
    void receive_{{ MSG_TYPE }}({{ MSG_TYPE }} *message) {
        {{ CLASS_NAME }}* deviceState = this;
        {{ pin['on_receive'] }}

    }
    {% endfor %}
#}

};

{% endfor %}
