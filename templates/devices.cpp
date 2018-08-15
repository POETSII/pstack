// State classes

@ for device in graph_type['device_types']

    @ set state_class = get_state_class(graph_type["id"], device['id'])
    @ set state = device['state']

    class {{ state_class }} {

    public:

        {{ lmap(declare_variable, state['scalars']) }}
        {{ lmap(declare_variable, state['arrays']) }}

        {{ state_class }} (){
            @ for scalar in state['scalars']
                this->{{ scalar['name'] }} = {{ scalar['default'] or "0" }};
            @ endfor
        }

        void print() {
            @ for name in state['scalars'] | map(attribute='name')
                @ set separator = '' if loop.last else ', '
                cprintf("{{ name }} = %d{{ separator }}", this->{{ name }});
            @ endfor

            cprintf("\n");
        }

    };

@ endfor

// Property classes

@ for device in graph_type['device_types']

    @ set props_class = get_props_class(graph_type["id"], device['id'])
    @ set props = device['properties']

    class {{ props_class }} {

    public:

        {{ lmap(declare_variable, props['scalars']) }}

        void set ({{- make_argument_list(props['scalars']) -}}) {
            @ for name in props['scalars'] | map(attribute='name')
                this->{{ name }} = {{ name }};
            @ endfor
        };

    };

@ endfor

// Device classes

@ for device in graph_type['device_types']

    @ set device_class = get_device_class(device['id'])
    @ set state_class = get_state_class(graph_type["id"], device['id'])
    @ set props_class = get_props_class(graph_type["id"], device['id'])
    @ set props = device['properties']

    class {{ device_class }}: public device_t {

    private:

        {{ state_class }} state;
        {{ props_class }} props;
        int rts;

    public:

        {{ device_class}} () {

            // Initialize array of destination lists

            this->dsts = new dst_list_t[{{ device['output_pins'] | count }}];
            this->rts = 0;

        };

        ~{{ device_class}}() {
        }

        void setProperties({{- make_argument_list(props['scalars']) -}}) {

            @ for name in props['scalars'] | map(attribute='name')
                props.{{ name }} = {{ name }};
            @ endfor
        }

        int getOutputPortCount() {
            return {{ device['output_pins'] | count }};
        }

        const char* getOutputPortName(int port_id) {

            @ for pin in device['output_pins']

                if (port_id == {{ loop.index0 }}) return "{{ pin['name'] }}";

            @ endfor

        }

        const char* getInputPortName(int port_id) {

            @ for pin in device['input_pins']

                if (port_id == {{ loop.index0 }}) return "{{ pin['name'] }}";

            @ endfor

        }

        void init();
        void print();
        int get_rts();
        void compute_rts();
        void receive(int pin_id, msg_t *msg);
        msg_t* send(int pin_id);

    };

@ endfor

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
