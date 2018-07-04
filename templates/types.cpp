// Base types

class state_t {
    // Base device state type
};

class props_t {
    // Base device properties type
};

class msg_t {
    // Base message type
};

// Convenient definition for message handler functions

typedef void (*handler_t) (state_t*, props_t*, msg_t*);

// Simulation types

struct device_t {
    state_t *state;
    props_t *props;
};

struct input_pin_t {
    handler_t *handler;
    device_t *device;
};

struct output_pin_t {
    input_pin_t *destinations;
    device_t *device;
};

struct delivery_t {
    msg_t *msg;
    output_pin_t *output_pin;
};
