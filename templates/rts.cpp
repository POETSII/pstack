typedef std::set<device_t*> rts_set_t;

void print_device_rts(device_t* dev) {

    int rts = (*dev).get_rts();
    int ports = (*dev).getOutputPortCount();

    if (rts == 0) {
        cprintf("Device <%s> no longer requests to send\n", dev->name.c_str());
        return;
    }

    for (int j=0; j<ports; j++) {

        if (rts & (1 << j)) {

            cprintf("Device <%s> requested to send on output port <%s>\n",
                dev->name.c_str(),
                (*dev).getOutputPortName(j)
            );

        }

    }

}

void print_rts_set(rts_set_t rts_set) {

    cprintf("Content of rts_set:");

    for (auto itr = rts_set.begin(); itr != rts_set.end(); ++itr)
        cprintf(" <%s>", (*itr)->name.c_str());
        // print_device_rts(*itr);

    cprintf("\n");


}

device_t* select_rts_device(rts_set_t rts_set) {

    if (rts_set.empty()) return NULL;

    return *(rts_set.begin());
}


int select_rts_port(device_t* dev) {

    int port_count = (*dev).getOutputPortCount();

    int rts = (*dev).get_rts();

    // loop through the bits of rts to find requested output port

    for (int j=0; j<port_count; j++)
        if (rts & (1 << j)) return j;

    // rts is not zero but no (valid) output port was determined, return -1 as
    // a special code for error

    return -1;
}
