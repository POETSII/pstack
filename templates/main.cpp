// vim: set ft=cpp:

#include <stdio.h>
#include <queue>

void handler_log(int level, const char *msg) {
    // do nothing
}

{{ graph_type['shared_code'] }}

{% include 'messages.cpp' %}
{% include 'devices.cpp' %}

void receive(node_t *state, req_t *msg) {
    printf("I received a message\n");
    (*msg).print();
    // state->counter += msg->content;
}

req_t get_trigger() {
    req_t result;
    // result.content = 1;
    return result;
}

int main() {

    node_t states[DEVICE_COUNT];

    req_t trigger = get_trigger();

    receive(&states[0], &trigger);

    printf("Content of state after receiving message:");

    states[0].print();

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