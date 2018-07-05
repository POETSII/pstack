// Handler functions

@ for device_type in graph_type['device_types']

@ set state_class = get_state_class(device_type['id'])
@ set props_class = get_props_class(device_type['id'])

    @ for pin in device_type['input_pins']

        @ set msg_class = get_msg_class(pin['message_type'])
        @ set handler = get_receive_handler_name(device_type['id'], pin['message_type'])

        void {{ handler }}(state_t *state, props_t *props, msg_t *msg) {
            {{ state_class }}* deviceState = ({{ state_class }}*) state;
            {{ props_class }}* deviceProperties = ({{ props_class}}*) props;
            {{ msg_class }} *message = ({{msg_class}}*) msg;
            {{ pin['on_receive'] }}

        }

    @ endfor

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

    int {{ get_rts_getter_name(device_type['id']) }}(state_t *state, props_t *props) {

        int result;
        int* readyToSend = &result;

        {{ state_class }}* deviceState = ({{ state_class }}*) state;
        {{ props_class }}* deviceProperties = ({{ props_class}}*) props;

        @ for out_pin in device_type['output_pins']
            @ set RTS_FLAG = get_rts_flag_variable(out_pin['name'])
            const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
        @ endfor

        {{ device_type['ready_to_send'] }}

        return result;
    }

@ endfor
