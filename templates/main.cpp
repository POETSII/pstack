// vim: set ft=cpp:

#include <stdio.h>
#include <queue>
#include <unordered_map>

@ include 'types.cpp'
@ include 'globals.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'
@ include 'shared.cpp'
@ include 'handlers.cpp'
@ include 'init.cpp'
@ include 'connections.cpp'

int main() {

    @ for group in graph_instance['devices'] | groupby('type')

        @ set devices = group.list
        @ set device_type = group.grouper
        @ set device_array = get_device_array(device_type)
        @ set device_init_func = get_init_function_name(device_type)

        device_t* {{ device_array }} = {{ device_init_func }}();

    @ endfor

    // Add edges

    @ set device_types = unique(graph_instance['devices'] | map(attribute='type'))
    @ set device_type_arrays = pymap(get_device_array, device_types)
    @ set add_edges_args = device_type_arrays | join(', ')

    add_edges({{ add_edges_args }});

    // ---- BEGIN RTS SCAN ----

    @ for group in graph_instance['devices'] | groupby('type')

        @ set devices = group.list
        @ set device_type = group.grouper
        @ set rts_handler = get_rts_getter_name(device_type)
        @ set device_array = get_device_array(device_type)

        for (int i=0; i<{{ devices | count }}; i++){

            device_t* dev = {{ device_array }} + i;

            int rts = {{ device_array }}[i].get_rts();

            printf("rts[%d]: 0x%x\n", i, rts);

            @ set device_type_obj = schema.get_device_type(device_type)

            for (int j=0; j<(*dev).getOutputPortCount(); j++) {

                if (rts & (1 << j)) {

                    printf("  - %s\n", (*dev).getOutputPortName(j));

                    msg_t* outgoing = {{ device_array }}[i].send(j);

                    printf("Outgoing message (filled):\n"); (*outgoing).print();

                }

            }

        }

    @ endfor

    // ---- END RTS SCAN ----

    // ---- BEGIN DELIVERY ----

    @ set total_devices = graph_instance['devices']|count

    state_t* all_states[{{ total_devices }}];

    // printf("queue size = %d\n", msg_q.size());
    // deliverable dv = msg_q.front();
    // msg_t* msg = dv.msg;

    // printf("source device index = %d\n", msg->_src_device_index);
    // printf("source device port = %d\n", msg->_src_device_port);

    @ set edges = graph_instance["edges"]

    // ---- END DELIVERY ----

    // typedef std::list<state_handler_tup> mylist ;

    // std::unordered_map<std::string, mylist> map1;

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


    return 0; }