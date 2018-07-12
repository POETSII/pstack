// Handler functions

@ for device_type in graph_type['device_types']

@ set device_class = get_device_class(device_type['id'])
@ set state_class = get_state_class(device_type['id'])
@ set props_class = get_props_class(device_type['id'])

    {% macro include_handler_defs() %}
        {{ state_class }}* deviceState = &state;
        {{ props_class }}* deviceProperties = &props;
    {% endmacro %}

    {% macro include_rts_constants() %}
        @ for out_pin in device_type['output_pins']
            @ set RTS_FLAG = get_rts_flag_variable(out_pin['name'])
            @ set RTS_FLAG_OBSOLETE = get_rts_flag_obsolete_variable(device_type['id'], out_pin['name'])
            const int {{ RTS_FLAG }} = 1 << {{ loop.index0 }};
            const int {{ RTS_FLAG_OBSOLETE }} = 1 << {{ loop.index0 }};
        @ endfor
    {% endmacro %}

    void {{ device_class }}::receive(int pin_id, msg_t *msg) {

        {{ include_handler_defs() }}
        {{ include_rts_constants() }}

        @ for pin in device_type['input_pins']

        if (pin_id == {{ loop.index0 }}) {

            @ set msg_class = get_msg_class(pin['message_type'])

            {{ msg_class }} *message = ({{ msg_class }}*) msg;

            {{ pin['on_receive'] or "// no handler code" }}

            compute_rts();

            return;

        }

        @ endfor

    }

    msg_t* {{ device_class }}::send(int pin_id) {

        {{ include_handler_defs() }}
        {{ include_rts_constants() }}

        @ for pin in device_type['output_pins']

            if (pin_id == {{ loop.index0 }}) {

                @ set msg_class = get_msg_class(pin['message_type'])

                {{ msg_class }} *message = new {{ msg_class }}();

                {{ pin['on_send'] or "// no handler code" }}

                compute_rts();

                return message;
            }

        @ endfor

    }

    void {{ device_class }}::init() {

        @ set init_pin = schema.get_pin(device_type['id'], '__init__')

        {{ include_handler_defs() }}
        {{ include_rts_constants() }}

        {{ init_pin['on_receive'] if init_pin else '' }}

        compute_rts();

    }

    void {{ device_class }}::compute_rts() {

        int* readyToSend = &rts;

        {{ include_handler_defs() }}
        {{ include_rts_constants() }}
        {{ device_type['ready_to_send'] or "// no handler code" }}

    }

    int {{ device_class }}::get_rts() {
        return rts;
    }

    void {{ device_class }}::print() {

        state.print();
    }

@ endfor
