// Handler functions

@ for device_type in graph_type['device_types']

@ set device_class = get_device_class(device_type['id'])
@ set state_class = get_state_class(device_type['id'])
@ set props_class = get_props_class(device_type['id'])

    @ for pin in device_type['output_pins']

        @ set msg_class = get_msg_class(pin['message_type'])
        @ set handler = get_send_handler_name(device_type['id'], pin['message_type'])

        void {{ handler }}(state_t *state, props_t *props, msg_t *msg) {
            {{ state_class }}* deviceState = ({{ state_class }}*) state;
            {{ props_class }}* deviceProperties = ({{ props_class}}*) props;
            {{ msg_class }} *message = ({{msg_class}}*) msg;
            {{ pin['on_send'] }}

        }

    @ endfor

    void {{ device_class }}::receive(int pin_id, msg_t *msg) {

        {{ state_class }}* deviceState = ({{ state_class }}*) state;
        {{ props_class }}* deviceProperties = ({{ props_class}}*) props;

        @ for pin in device_type['input_pins']

        if (pin_id == {{ loop.index0 }}) {

            @ set msg_class = get_msg_class(pin['message_type'])

            {{ msg_class }} *message = ({{ msg_class }}*) msg;

            {{ pin['on_receive'] }}

            return;

        }

        @ endfor

    }

    void {{ device_class }}::init() {

        @ set pin_map = dict_from_list(device_type['input_pins'], 'name')

        @ set init_pin = pin_map.get('__init__')

        {{ state_class }}* deviceState = ({{ state_class }}*) this->state;
        {{ props_class }}* deviceProperties = ({{ props_class}}*) this->props;

        {{ init_pin['on_receive'] if init_pin else '' }}

    }

@ endfor
