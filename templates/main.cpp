// vim: set ft=cpp:

#include <stdio.h>
#include <queue>
#include <unordered_map>

@ include 'types.cpp'
@ include 'globals.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'

{{ graph_type['shared_code'] }}

@ include 'handlers.cpp'
@ include 'init.cpp'

int main() {

    @ for group in graph_instance['devices']|groupby('type')

    @ set devices = group.list
    @ set device_type = group.grouper
    @ set device_array = get_device_array(device_type)
    @ set device_init_func = get_init_function_name(device_type)

    device_t* {{ device_array }} = {{ device_init_func }}();

    @ endfor

    // ---- BEGIN RTS SCAN ----

    @ for group in graph_instance['devices']|groupby('type')

    @ set devices = group.list
    @ set device_type = group.grouper
    @ set device_array = get_device_array(device_type)

    for (int i=0; i<{{ devices|count }}; i++){

        int rts = {{ get_rts_getter_name(device_type) }}({{ device_array }}[i].state, {{ device_array }}[i].props);

        printf("rts[%d]: 0x%x\n", i, rts);

        @ set device_type_obj = graph_type['device_types']|selectattr('id', 'equalto', device_type)|first

        @ for output_pin in device_type_obj['output_pins']

        @ set msg_class = get_msg_class(output_pin['message_type'])

        if (rts & (1 << {{ loop.index0 }})) {

            printf("  - {{ output_pin['name'] }}\n");

            {{ msg_class }}* outgoing = new {{ msg_class }}();

            handler_t handler = &{{ get_send_handler_name(device_type, output_pin['message_type']) }};

            handler({{ device_array }}[i].state, {{ device_array }}[i].props, outgoing);

            printf("Outgoing message (filled):\n"); (*outgoing).print();

            msg_t* outgoing_base = (msg_t*) outgoing;

            // outgoing_base->_src_device_index = i;
            // outgoing_base->_src_device_port = {{ loop.index0 }};

            // deliverable dv;
            // dv.msg = outgoing_base;

            // msg_q.push(dv);

        }

        @ endfor

    }

    @ endfor

    // ---- END RTS SCAN ----

    // ---- BEGIN DELIVERY ----

    @ set total_devices = graph_instance['devices']|count

    state_t* all_states[{{ total_devices }}];

    int* int_arr[] {
        new int[3] {1, 2, 3},
        new int[4] {1, 2, 3, 4}
    };

    handler_t handlers[][2] = {
        {
            &{{ get_receive_handler_name('node_a', 'req') }},
            &{{ get_receive_handler_name('node_a', 'ack') }}
        }
    };

    // printf("queue size = %d\n", msg_q.size());
    // deliverable dv = msg_q.front();
    // msg_t* msg = dv.msg;

    // printf("source device index = %d\n", msg->_src_device_index);
    // printf("source device port = %d\n", msg->_src_device_port);

    @ set edges = graph_instance["edges"]

    // ---- END DELIVERY ----

    // typedef std::list<state_handler_tup> mylist ;

    // std::unordered_map<std::string, mylist> map1;

    // destination *myd[10];

    // myd[0] = new destination[5];
    // myd[1] = new destination[4];

    /*

    @ set incoming_index = build_index(edges|map(attribute='dst'))

    {{ incoming_index|pprint }}

    */

    // Section A -----------

    // const int src_ind = msg->_src_device_index;
    // const int src_por = msg->_src_device_port;

    const int src_ind = 0;
    const int src_por = 0;

    @ for device in graph_instance['devices']

    @ set device_type = device['type']
    @ set PROP_ARR = get_properties_array(device_type)
    @ set STAT_ARR = get_state_array(device_type)
    @ set device_type_obj = graph_type['device_types']|selectattr('id', 'equalto', device_type)|first
    @ set outer_loop = loop

    @ for output_pin in device_type_obj['output_pins']

    @ set src = (device['id'], output_pin['name'])

    @ set key = device['id'] + '-' + output_pin['name']

    // {{ src[0], src[1], output_pin['message_type'] }} -> {{ ( edges | selectattr('src', 'equalto', src) | map(attribute='dst') | list ) }}

    if (src_ind == {{ outer_loop.index0 }} && src_por == {{ loop.index0 }}){

        @ set inbound = edges | selectattr('src', 'equalto', src) | map(attribute='dst') | list

        @ for in_dev, in_port in inbound
        @ set in_dev_type = graph_instance['devices'] | selectattr('id', 'equalto', in_dev) | first
        @ set r_handler = get_receive_handler_name(in_dev_type, msg_type)
        // do something with {{ in_dev }} and {{ in_port }}
        // {{ in_dev_type }}
        @ endfor

    }

    @ endfor

    @ endfor

    // end of Section A ---------

    // queue <state> q;
    // state *s1 = states;
    // s1->x = 5;
    // q.push(*s1);
    // state t = q.front();
    // printf("queue size = %d\n", q.size());
    // q.pop();
    // printf("queue size = %d\n", q.size());
    // printf("hello %d\n", t.x);

    return 0;
}