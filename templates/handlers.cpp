// Handler functions

@ for device_type in graph_type['device_types']

@ set device_class = get_device_class(device_type['id'])
@ set state_class = get_state_class(device_type['id'])
@ set props_class = get_props_class(device_type['id'])

    {% macro include_handler_defs() %}
        // {{ state_class }}* deviceState = ({{ state_class }}*) this->state;
        // {{ props_class }}* deviceProperties = ({{ props_class}}*) this->props;

        {{ state_class }}* deviceState = &state;
        {{ props_class }}* deviceProperties = &props;

    {% endmacro %}

    void {{ device_class }}::receive(int pin_id, msg_t *msg) {

        {{ include_handler_defs() }}

        @ for pin in device_type['input_pins']

        if (pin_id == {{ loop.index0 }}) {

            @ set msg_class = get_msg_class(pin['message_type'])

            {{ msg_class }} *message = ({{ msg_class }}*) msg;

            {{ pin['on_receive'] }}

            compute_rts();

            return;

        }

        @ endfor

    }

    msg_t* {{ device_class }}::send(int pin_id) {

        {{ include_handler_defs() }}

        @ for pin in device_type['output_pins']

            if (pin_id == {{ loop.index0 }}) {

                @ set msg_class = get_msg_class(pin['message_type'])

                {{ msg_class }} *message = new {{ msg_class }}();

                {{ pin['on_send'] }}

                return message;

            }

        @ endfor

    }

    void {{ device_class }}::init() {

        @ set init_pin = schema.get_pin(device_type['id'], '__init__')

        {{ include_handler_defs() }}

        {{ init_pin['on_receive'] if init_pin else '' }}

        compute_rts();

    }

    void {{ device_class }}::compute_rts() {

        int* readyToSend = &rts;

        {{ include_handler_defs() }}

        @ for out_pin in device_type['output_pins']
            @ set RTS_FLAG = get_rts_flag_variable(out_pin['name'])
            const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
        @ endfor

        {{ device_type['ready_to_send'] }}

    }

    int {{ device_class }}::get_rts() {
        return rts;
    }

    void {{ device_class }}::print() {

        state.print();
    }

@ endfor
