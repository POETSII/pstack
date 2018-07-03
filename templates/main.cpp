// vim: set ft=cpp:

#include <stdio.h>
#include <queue>

@ include 'globals.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'
{{ graph_type['shared_code'] }}
@ include 'handlers.cpp'

typedef void (*handler_t) (state_t*, prop_t*, msg_t*);

int main() {

    @ include 'init.cpp'

    for (int i=0; i<5; i++){
        printf("Device %d:\n", i);
        deviceStates_node[i].print();
    }

    // ---- BEGIN RTS SCAN ----

    @ for group in graph_instance['devices']|groupby('type')

    @ set device_type = group.grouper
    @ set devices = group.list
    @ set PROP_ARR = "deviceProperties_" + device_type
    @ set STAT_ARR = "deviceStates_" + device_type

    for (int i=0; i<{{ devices|count }}; i++){

        int rts = {{ get_rts_getter_name(device_type) }}({{ STAT_ARR }} + i, {{ PROP_ARR }} + i);

        printf("rts[%d]: 0x%x\n", i, rts);

        @ set device_type_obj = graph_type['device_types']|selectattr('id', 'equalto', device_type)|first

        @ for output_pin in device_type_obj['output_pins']

        @ set msg_class = get_msg_class(output_pin['message_type'])

        if (rts & (1 << {{ loop.index0 }})) {

            printf(" - {{ output_pin['name'] }}\n");

            {{ msg_class }}* outgoing = new {{ msg_class }}();

            handler_t handler = &{{ get_send_handler_name(device_type, output_pin['message_type']) }};

            handler({{ STAT_ARR }} + i, {{ PROP_ARR }} + i, outgoing);

            printf("Outgoing message (filled):\n"); (*outgoing).print();

        }

        @ endfor

    }

    @ endfor

    // ---- END RTS SCAN ----

    handler_t handlers[][2] = {
        {
            &{{ get_receive_handler_name('node', 'req') }},
            &{{ get_receive_handler_name('node', 'ack') }}
        }
    };

    // queue <state> q;
    // state *s1 = states;
    // s1->x = 5;
    // printf("queue size = %d\n", q.size());
    // q.push(*s1);
    // state t = q.front();
    // printf("queue size = %d\n", q.size());
    // q.pop();
    // printf("queue size = %d\n", q.size());
    // printf("hello %d\n", t.x);

    return 0;
}