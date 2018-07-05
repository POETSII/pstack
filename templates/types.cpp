// Base types

class state_t {
    // Base device state type

    virtual void test() = 0;
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

class device_t {
public:
    state_t *state;
    props_t *props;
    virtual int get_rts() = 0;
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
