// Device state types

@ for device in graph_type['device_types']

    @ set state_class = get_state_class(device['id'])
    @ set state = device['state']

    class {{ state_class }}: public state_t {

    public:

        void test() {

        }

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
            {{- make_argument_list(props['scalars']) -}}
        ) {
            set({{- make_argument_list(props['scalars'], include_types=False) -}});
        };

        void set (
            {{- make_argument_list(props['scalars']) -}}
        ) {
            @ for scalar_name in props['scalars'] | map(attribute='name')
                this->{{ scalar_name }} = {{ scalar_name }};
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

        {{ device_class}} (
            {{- make_argument_list(props['scalars']) -}}
        ) {
            state = new {{ state_class }}();

            props = new {{ props_class }}(
                {{- make_argument_list(props['scalars'], include_types=False) -}}
            );

        };

        {{ device_class}} () {
            state = new {{ state_class }}();
            props = new {{ props_class }}();

        };

        ~{{ device_class}}() {
            delete state;
            delete props;
        }


        void setProperties({{- make_argument_list(props['scalars']) -}}) {

            {{ props_class }} *myProps = ({{ props_class }}*) this->props;

            @ for scalar_name in props['scalars'] | map(attribute='name')
                myProps->{{ scalar_name }} = {{ scalar_name }};
            @ endfor
        }

        int get_rts() {

            int result;
            int* readyToSend = &result;

            {{ state_class }}* deviceState = ({{ state_class }}*) this->state;
            {{ props_class }}* deviceProperties = ({{ props_class }}*) this->props;

            @ for out_pin in device['output_pins']
                @ set RTS_FLAG = get_rts_flag_variable(out_pin['name'])
                const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
            @ endfor

            {{ device['ready_to_send'] }}

            return result;
        }

        void init();
        void receive(int pin_id, msg_t *msg);

    };

@ endfor