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
    virtual const char* getInputPortName(int) = 0;

    dst_list_t* getPortDestinations(int port_id) {
        return dsts + port_id;
    }

};

class delivery_t {

public:

    msg_t *msg;
    dst_list_t dst;

    delivery_t(msg_t* msg, dst_list_t dst) {
        this->msg = msg;
        this->dst = dst;
    }

    void print() {

        printf("Deliverying the following message:\n");

        (*msg).print();

        printf("To the following nodes:\n");

        for (int i=0; i<dst.size(); i++) {

            destination_t dest = dst.at(i);
            device_t* dest_dev = (device_t*) dest.device;
            int dest_port = dest.port;

            printf("  - node <%s> (input port <%s>)\n",
                (*dest_dev).name.c_str(),
                (*dest_dev).getInputPortName(dest_port)
            );
        }

    }
};
