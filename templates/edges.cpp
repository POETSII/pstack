void add_edges(std::vector<device_t*> devices, uint32_t simulation_region) {

    @ set connections = schema.get_edge_table()
    @ set ncons = connections | count

    int edges[{{ ncons }}][5] = {

        @ for row in connections
            { {{- row | join(', ') -}} } {{ ',' if not loop.last else '' }}
        @ endfor

    };

    for (int i=0; i<{{ ncons }}; i++) {

        device_t* src_dev = devices[edges[i][0]];
        device_t* dst_dev = devices[edges[i][1]];

        int src_pin = edges[i][2];
        int dst_pin = edges[i][3];

        uint32_t dst_dev_region = edges[i][4];

        reg_set_t *regs = (*src_dev).getPortOutputRegions(src_pin);

        if (dst_dev_region != simulation_region)
            (*regs).insert(dst_dev_region); // add external region

        if (dst_dev_region != simulation_region)
            continue; // don't add external devices as local destinations

        dst_list_t *dsts = (*src_dev).getPortDestinations(src_pin);

        (*dsts).push_back(destination_t(dst_dev, dst_pin));
    }

    return;

}
