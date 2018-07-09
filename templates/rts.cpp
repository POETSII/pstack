typedef std::set<device_t*> rts_set_t;

void print_device_rts(device_t* dev) {

    int rts = (*dev).get_rts();
    int ports = (*dev).getOutputPortCount();

    if (rts == 0) {
        printf("Device <%s> no longer requests to send\n", dev->name.c_str());
        return;
    }

    for (int j=0; j<ports; j++) {

        if (rts & (1 << j)) {

            printf("Device <%s> requested to send on output port <%s>\n",
                dev->name.c_str(),
                (*dev).getOutputPortName(j)
            );

        }

    }

}

void print_rts_set(rts_set_t rts_set) {

    printf("Content of rts_set:\n");

    for (auto itr = rts_set.begin(); itr != rts_set.end(); ++itr)
        print_device_rts(*itr);

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
