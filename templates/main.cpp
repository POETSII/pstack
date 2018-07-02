// vim: set ft=cpp:

#include <stdio.h>
#include <queue>

void handler_log(int level, const char *msg, ...) {
    // do nothing
}

void handler_exit(int exitCode) {
    // do nothing
}

{% include 'messages.cpp' %}

{% include 'devices.cpp' %}

{{ graph_type['shared_code'] }}

{% include 'handlers.cpp' %}

void receive(node_state_t *state, req_t *msg) {
    printf("I received a message\n");
    (*msg).print();
    // state->counter += msg->content;
}

int main() {

    {% include 'init.cpp' %}

    printf("Content of state after receiving message:\n");

    deviceStates_node[0].print();

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