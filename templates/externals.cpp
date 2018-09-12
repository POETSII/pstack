
int receive_externals(std::vector<device_t*> &devices, std::vector<delivery_t> &dlist) {

	cprintf("Waiting for external messages ...\n");

	char input[256];

	uint32_t device_id;
	uint32_t port;
	uint32_t msg_type_id;

	cprintf("Enter (device_id, port, msg_type_id, fields ...): ");

	scanf("%d", &device_id);
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

    cprintf("Created new delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

    // new_dv.print();

    dlist.push_back(new_dv);

	return 0;
}

