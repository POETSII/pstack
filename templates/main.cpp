#include <stdio.h>
#include <queue>

#define DEVICE_COUNT 10

class state_t {

public:

    int x;
    int y;
    int counter;

    void print() {
        printf("x = %d\n", this->x);
        printf("y = %d\n", this->y);
        printf("counter = %d\n", this->counter);
    }
};

class msg_t {

public:

    int content;

    void print() {
        printf("content = %d\n", this->content);
    }
};

void init_state(state_t *state) {
    state->x = 0;
    state->y = 0;
    state->counter = 0;
}

void print_state(state_t *state) {
}

void receive(state_t *state, msg_t *msg) {
    printf("I received a message\n");
    (*msg).print();
    state->counter += msg->content;
}

msg_t get_trigger() {
    msg_t result;
    result.content = 1;
    return result;
}

int main() {

    state_t states[DEVICE_COUNT];

    for (int i=0; i<DEVICE_COUNT; i++)
        init_state(&states[i]);

    // for (int i=0; i<DEVICE_COUNT; i++)
    //     print_state(&states[i]);

    msg_t trigger = get_trigger();

    receive(&states[0], &trigger);

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