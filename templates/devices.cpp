// State classes

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
            @ for name in state['scalars'] | map(attribute='name')
                printf("  - {{ name }} = %d\n", this->{{ name }});
            @ endfor
        }

    };

@ endfor

// Property classes

@ for device in graph_type['device_types']

    @ set props_class = get_props_class(device['id'])
    @ set props = device['properties']

    class {{ props_class }}: public props_t {

    public:

        {{ lmap(declare_variable, props['scalars']) }}

        {{ props_class}} ({{- make_argument_list(props['scalars']) -}}) {
            set({{- make_argument_list(props['scalars'], include_types=False) -}});
        };

        void set ({{- make_argument_list(props['scalars']) -}}) {
            @ for name in props['scalars'] | map(attribute='name')
                this->{{ name }} = {{ name }};
            @ endfor
        };

        {{ props_class}} () {};

    };

@ endfor

// Device classes

@ for device in graph_type['device_types']

    @ set device_class = get_device_class(device['id'])
    @ set state_class = get_state_class(device['id'])
    @ set props_class = get_props_class(device['id'])
    @ set props = device['properties']

    class {{ device_class }}: public device_t {

    public:

        {{ device_class}} () {
            state = new {{ state_class }}();
            props = new {{ props_class }}();

            // Initialize array of destination lists

            this->dsts = new dst_list_t[{{ device['output_pins'] | count }}];

        };

        ~{{ device_class}}() {
            delete state;
            delete props;
        }

        void setProperties({{- make_argument_list(props['scalars']) -}}) {

            {{ props_class }} *myProps = ({{ props_class }}*) this->props;

            @ for name in props['scalars'] | map(attribute='name')
                myProps->{{ name }} = {{ name }};
            @ endfor
        }

        int getOutputPortCount() {
            return {{ device['output_pins'] | count }};
        }

        void init();
        int get_rts();
        void receive(int pin_id, msg_t *msg);
        msg_t* send(int pin_id);

    };

@ endfor