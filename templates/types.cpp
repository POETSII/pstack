// cprintf (conditional printf): simple function that either passes arguments
// or does nothing, depending on the flag `print_debug`.

int print_debug = {{ '1' if options['debug'] else '0' }};

void cprintf(const char *fmt, ...) {

    if (!print_debug)
        return;

    va_list va;
    va_start (va, fmt);
    vprintf (fmt, va);
    va_end (va);
}

// Base types

class msg_t {
    // Base message type
public:
    virtual void print() = 0;
    virtual const char* getName() = 0;
    virtual void serialize(char *buf) = 0;
    virtual void deserialize(char *buf) = 0;
    virtual int getByteCount() = 0;
};

// Simulation types

class destination_t {

public:

    void *device = NULL;
    int port;

    destination_t(void *device, int port) {
        this->device = device;
        this->port = port;
    }

    void print();

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
    virtual const char* getInputPortName(int) = 0;

    dst_list_t* getPortDestinations(int port_id) {
        return dsts + port_id;
    }

};

void destination_t::print() {

    device_t* device = (device_t*) (this->device);

    cprintf("  - Destination: device <%s> (input port <%s>)\n",
        (*device).name.c_str(),
        (*device).getInputPortName(port)
    );
}

class delivery_t {

public:

    device_t *origin;
    msg_t *msg;
    dst_list_t dst;

    delivery_t(msg_t* msg, dst_list_t dst, device_t *origin) {
        this->origin = origin;
        this->msg = msg;
        this->dst = dst;
    }

    void print_destinations() {
        for (int i=0; i<dst.size(); i++) {
            destination_t dest = dst.at(i);
            device_t* dev = (device_t*) dest.device;
            cprintf("<%s> ", dev->name.c_str());
        }
        cprintf("\n");
    }

    void print() {
        cprintf("Delivery of the following <%s> message:\n", (*msg).getName());
        (*msg).print();
        cprintf("To the following nodes:\n");
        for (int i=0; i<dst.size(); i++) {
            destination_t dest = dst.at(i);
            dest.print();
        }
    }
};
