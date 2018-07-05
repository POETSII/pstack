// Device state types

@ for device in graph_type['device_types']

    @ set state_class = get_state_class(device['id'])
    @ set state = device['state']

    class {{ state_class }}: public state_t {

    public:

        {{ lmap(declare_variable, state['scalars']) }}
        {{ lmap(declare_variable, state['arrays']) }}

        {{ state_class }} (){
            @ for scalar in state['scalars']
                this->{{ scalar['name'] }} = 0;
            @ endfor
        }

        void print() {
            @ for scalar_name in state['scalars'] | map(attribute='name')
                printf("  - {{ scalar_name }} = %d\n", this->{{ scalar_name }});
            @ endfor
        }

    };

@ endfor

// Device property types

@ for device in graph_type['device_types']

    @ set props_class = get_props_class(device['id'])
    @ set props = device['properties']

    class {{ props_class }}: public props_t {

    public:

        {{ lmap(declare_variable, props['scalars']) }}

        {{ props_class}} (
            {{ make_argument_list(props['scalars']) }}
        ) {
            @ for scalar_name in props['scalars'] | map(attribute='name')
                this->{{ scalar_name }} = {{ scalar_name }};
            @ endfor
        };

    };

@ endfor
