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

typedef std::set<device_t*> rts_set_t;

void print_rts_set(rts_set_t rts_set) {

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

}

device_t* select_rts_device(rts_set_t rts_set) {

    return *(rts_set.begin());
}

int select_rts_port(device_t* dev) {

    int port_count = (*dev).getOutputPortCount();

    int rts = (*dev).get_rts();

    for (int j=0; j<port_count; j++) {

        if (rts & (1 << j)) return j;

    }

}

int main() {

    std::vector<device_t*> devices;
    std::vector<delivery_t> dlist; // delivery list

    @ set device_types = unique(graph_instance['devices'] | map(attribute='type'))
    @ set init_funcs = pymap(get_init_function_name, device_types)
    @ set init_calls = mformat("%s(devices);", init_funcs) | join("\n")

    {{ init_calls }}

    add_edges(devices);

    rts_set_t rts_set;

    // ---- BEGIN RTS SCAN ----

    for (int i=0; i<devices.size(); i++){

        device_t* dev = devices[i];

        int rts = (*dev).get_rts();

        if (rts) rts_set.insert(dev);

    }

    // ---- END RTS SCAN ----

    printf("----\n");

    print_rts_set(rts_set);

    printf("----\n");

    device_t* dev = select_rts_device(rts_set);

    int port = select_rts_port(dev);

    printf("Device <%s> requested to send on output port %d <%s>\n", dev->name.c_str(), port, (*dev).getOutputPortName(port));

    dst_list_t *dests = (*dev).getPortDestinations(port);

    printf("Destinations: %d\n", (*dests).size());

    for (int i=0; i<(*dests).size(); i++) {
        destination_t dest = (*dests).at(i);
        device_t* dest_dev = (device_t*) dest.device;
        int dest_port = dest.port;
        printf("  - node <%s> port %d <%s>\n", (*dest_dev).name.c_str(), dest_port, (*dest_dev).getInputPortName(dest_port));

    }

    // Create message by calling send handler

    msg_t* msg = (*dev).send(port);
    printf("message:\n");
    (*msg).print();

    // Create delivery object

    dlist.push_back(delivery_t(msg, *dests));

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