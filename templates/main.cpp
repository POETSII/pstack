// vim: set ft=cpp:

#include <stdio.h>
#include <queue>
#include <set>
#include <unordered_map>
#include <string>

@ include 'types.cpp'
@ include 'globals.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'
@ include 'shared.cpp'
@ include 'handlers.cpp'
@ include 'init.cpp'
@ include 'connections.cpp'

int main() {

    std::vector<device_t*> devices;

    @ for group in graph_instance['devices'] | groupby('type')

        @ set devices = group.list
        @ set device_type = group.grouper
        @ set device_array = get_device_array(device_type)
        @ set device_init_func = get_init_function_name(device_type)
        @ set device_class = get_device_class(device_type)

        {{ device_init_func }}(devices);

    @ endfor

    // Add edges

    @ set device_types = unique(graph_instance['devices'] | map(attribute='type'))
    @ set device_type_arrays = pymap(get_device_array, device_types)
    @ set add_edges_args = device_type_arrays | join(', ')

    add_edges(devices);

    std::set<device_t*> rts_set;

    // ---- BEGIN RTS SCAN ----

    for (int i=0; i<devices.size(); i++){

        device_t* dev = devices[i];

        int rts = (*dev).get_rts();

        if (rts) rts_set.insert(dev);

    }

    // ---- END RTS SCAN ----

    for (auto itr = rts_set.begin(); itr != rts_set.end(); ++itr) {

        device_t* dev = *itr;

        int rts = (*dev).get_rts();

        for (int j=0; j<(*dev).getOutputPortCount(); j++) {

            if (rts & (1 << j)) {

                printf("Device <%s> requested to send on output port <%s>\n", dev->name.c_str(), (*dev).getOutputPortName(j));

                // msg_t* outgoing = (*dev).send(j);

                // printf("Outgoing message (filled):\n"); (*outgoing).print();

            }

        }
    }


    // ---- BEGIN DELIVERY ----

    // @ set total_devices = graph_instance['devices']|count

    // state_t* all_states[{{ total_devices }}];

    // printf("queue size = %d\n", msg_q.size());
    // deliverable dv = msg_q.front();
    // msg_t* msg = dv.msg;

    // printf("source device index = %d\n", msg->_src_device_index);
    // printf("source device port = %d\n", msg->_src_device_port);

    // @ set edges = graph_instance["edges"]

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