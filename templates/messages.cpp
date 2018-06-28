// Message types

{% for message in graph_type['message_types'] %}
{%- set CLASS_NAME = message['id'] + "_t" -%}
class {{ CLASS_NAME }} {

public:

    {% for scalar in message['fields']['scalars'] %}
    {{- scalar['type'] }} {{ scalar['name'] }};
    {% endfor %}

    {{ CLASS_NAME }} (){
    {% for scalar in message['fields']['scalars'] %}
        this->{{ scalar['name'] }} = 0;
    {%- endfor %}
    }

    void print() {
    {% for scalar in message['fields']['scalars'] %}
        printf("{{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
    {%- endfor %}
    }
};

{% endfor %}
