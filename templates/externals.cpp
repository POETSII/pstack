int receive_externals(std::vector<device_t*> &devices, std::vector<delivery_t> &dlist) {

	// Receive message from remote region and add it to dlist.

	// Return 0 if successful, 1 if shutdown signal was received or error was
	// encountered while processing the incoming message.

	cprintf("Waiting for external messages ...\n");

	char input[256];

	int device_id;
	uint32_t port;
	uint32_t msg_type_id;

	cprintf("Enter (device_id, port, msg_type_id, fields ...):\n");

	scanf("%d", &device_id);


	if (device_id == -1) // special code for shutdown
		return 1;

	if ((device_id < -1) || (device_id >= devices.size())) {
		printf("External message contains invalid device id %d\n", device_id);
		return 1;
	}

	scanf("%d", &port);
	scanf("%d", &msg_type_id);

	cprintf("Checking message type ...\n");

	msg_t* msg = NULL;

	@ for message in graph_type['message_types']

		@ set msg_class = get_msg_class(graph_type["id"], message['id'])

		if (msg_type_id == {{ loop.index0 }})
			msg = new {{ msg_class }}();

	@ endfor

	if (msg == NULL) {
		printf("External message contains invalid message type %d\n", msg_type_id);
		return 1;
	}

	device_t* dev = devices[device_id];

	if (port >= (*dev).getOutputPortCount()) {
		printf("External message contains invalid output port number (%d)\n", port);
		return 1;
	}

	(*msg).read_debug();

	dst_list_t *dests = (*dev).getPortDestinations(port);

	// Create delivery object

	delivery_t new_dv = delivery_t(msg, *dests, dev);

	cprintf("Created delivery\n");

	cprintf("Received remote delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

	dlist.push_back(new_dv);

	return 0;
}

int send_externals(uint32_t device_id, uint32_t port, msg_t* msg, reg_set_t* regions) {

	for (reg_set_t::iterator it = (*regions).begin(); it != (*regions).end(); ++it) {
		printf3("send %d %d %d %d", *it, device_id, port, msg->index);
		(*msg).print_debug();
		printf3("\n");
	}

}

void shutdown_externals(reg_set_t other_regions) {

	cprintf("Shutting down external regions\n");

	for (reg_set_t::iterator it = other_regions.begin(); it != other_regions.end(); ++it)
		printf3("send %d -1", *it);

}