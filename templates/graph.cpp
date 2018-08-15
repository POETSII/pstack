// Graph Type class

@ set graph_type_class = get_graph_type_props_class(graph_type['id'])
@ set props = graph_type['properties']

class {{ graph_type_class }} {

public:

    {{ lmap(declare_variable, props['scalars']) }}
    {{ lmap(declare_variable, props['arrays']) }}

    void set ({{- make_argument_list(props['scalars']) -}}) {
        @ for name in props['scalars'] | map(attribute='name')
            this->{{ name }} = {{ name }};
        @ endfor
    };

};

{{ graph_type_class }} *graphProperties;
