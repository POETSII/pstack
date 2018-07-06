#include<vector>

// Base types

class msg_t {
    // Base message type
public:
    virtual void print() = 0;
};

// Convenient definition for message handler functions

// Simulation types

class destination_t {
public:
    void *device = NULL;
    int port;
    destination_t(void *device, int port) {
        this->device = device;
        this->port = port;
    }
};

typedef std::vector<destination_t> dst_list_t;

class device_t {

private:

protected:
    dst_list_t* dsts; // destinations by output port

public:
    std::string name = "n/a";
    virtual void init() = 0;
    virtual void print() = 0;
    virtual int get_rts() = 0;
    virtual void receive(int, msg_t*) = 0;
    virtual msg_t* send(int) = 0;
    virtual int getOutputPortCount() = 0;
    virtual const char* getOutputPortName(int) = 0;

    dst_list_t getPortDestinations(int port_id) {
        return dsts[port_id];
    }

};

// struct input_pin_t {
//     handler_t *handler;
//     device_t *device;
// };

// struct output_pin_t {
//     input_pin_t *destinations;
//     device_t *device;
// };

struct delivery_t {
    msg_t *msg;
    destination_t *dst;
};
