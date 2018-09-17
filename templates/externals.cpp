int receive_externals(std::vector<device_t*> &devices, std::vector<delivery_t> &dlist) {

	// Receive message from remote region and add it to dlist.
	// Return 0 if successful, 1 if shutdown signal was received.

	cprintf("Waiting for external messages ...\n");

	char input[256];

	uint32_t device_id;
	uint32_t port;
	uint32_t msg_type_id;

	cprintf("Enter (device_id, port, msg_type_id, fields ...):\n");

	scanf("%d", &device_id);

	if (device_id == -1) // special code for shutdown
		return 1;

	scanf("%d", &port);
	scanf("%d", &msg_type_id);

	msg_t* msg = NULL;

	@ for message in graph_type['message_types']

	    @ set msg_class = get_msg_class(graph_type["id"], message['id'])

	    if (msg_type_id == {{ loop.index0 }})
	    	msg = new {{ msg_class }}();

	@ endfor

	if (msg == NULL)
		return 1; // invalid msg_type_id

	(*msg).read_debug();

    device_t* dev = devices[device_id];

    dst_list_t *dests = (*dev).getPortDestinations(port);

    // Create delivery object

    delivery_t new_dv = delivery_t(msg, *dests, dev);

    cprintf("Received remote delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

    // new_dv.print();

    dlist.push_back(new_dv);

	return 0;
}

int send_externals(uint32_t device_id, uint32_t port, msg_t* msg, reg_set_t* regions) {

	cprintf("  - Regions: ");

	for (reg_set_t::iterator it = (*regions).begin(); it != (*regions).end(); ++it)
	    cprintf("%d ", *it);

	cprintf("\n");

    // cprintf("Outgoing -> src = %d\n", device_id);
    // cprintf("Outgoing -> port = %d\n", port);
    // cprintf("Outgoing -> msg_type_id = %d\n", msg->index);
    // cprintf("Outgoing -> fields =\n");
    // (*msg).print();

    cprintf("  - Send: %d, %d, %d", device_id, port, msg->index);
    (*msg).print_debug();
    cprintf("\n");

}

void shutdown_externals(reg_set_t other_regions) {

	cprintf("Shutting down external regions\n");

	cprintf("  - Regions: ");

	for (reg_set_t::iterator it = other_regions.begin(); it != other_regions.end(); ++it)
		cprintf("%d", *it);

	cprintf("\n");
    cprintf("  - Send: -1\n");

}