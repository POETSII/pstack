// vim: set ft=cpp:

#include <stdio.h>
#include <queue>

{% include 'globals.cpp' %}
{% include 'messages.cpp' %}
{% include 'devices.cpp' %}
{{ graph_type['shared_code'] }}
{% include 'handlers.cpp' %}

int main() {

    {% include 'init.cpp' %}

    for (int i=0; i<5; i++){
        printf("Device %d:\n", i);
        deviceStates_node[i].print();
    }

    for (int i=0; i<5; i++){
        int rts = get_rts_node(deviceStates_node + i, deviceProperties_node + i);
        printf("rts[%d]: 0x%x\n", i, rts);
    }

    void (*funPtr1) (state_t*, prop_t*, msg_t*) = &{{ get_receive_handler_name('node', 'req') }};
    void (*funPtr2) (state_t*, prop_t*, msg_t*) = &{{ get_receive_handler_name('node', 'ack') }};

    // print_state(&states[0]);

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