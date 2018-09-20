struct remote_command_t {
	int type;           // command type: (0) message, (1) shutdown
	int device_id;      // remote device id
	int port;           // output port of remote device
	int nfields;        // number of field items
	int fields[100];    // message fields
};

remote_command_t read_remote_command() {

	remote_command_t rcmd;

	int first;
	int nfields;

	cprintf("Enter (device_id, port, nfields, fields...):\n");

	scanf("%d", &first);

	if (first == -1) {

		rcmd.type = 1; // shutdown command

	} else {

		rcmd.type = 0; // message command

		rcmd.device_id = first;

		scanf("%d %d", &(rcmd.port), &(rcmd.nfields));

		for (int i=0; i<rcmd.nfields; i++)
			scanf("%d", rcmd.fields + i);

	}

	return rcmd;

}

void print_remote_command(remote_command_t rcmd) {

	// Print content of remote command (for debugging).

	printf("Remote command:\n");

	printf("  - type: %d\n", rcmd.type);
	printf("  - device_id: %d\n", rcmd.device_id);
	printf("  - port: %d\n", rcmd.port);
	printf("  - fields (n = %d):\n", rcmd.nfields);

	for (int i=0; i<rcmd.nfields; i++)
		printf("    - [%d] = %d\n", i, rcmd.fields[i]);

}

bool is_valid_message_command(remote_command_t rcmd) {

	const int ndevices = {{ graph_instance['devices'] | count }};
	const int nmsgtypes = {{ graph_type['message_types'] | count }};

	if (rcmd.type != 0) {
		printf("External command does not contain message\n");
		return false; // not message command
	}

	if (rcmd.device_id<0 || rcmd.device_id>=ndevices) {
		printf("External message command contains incorrect device id (%d)\n", rcmd.device_id);
		return false; // invalid device id
	}

	return true;

}

int receive_externals(std::vector<device_t*> &devices, std::vector<delivery_t> &dlist) {

	// Receive external command

	// Return 0 if successful, 1 if shutdown signal was received or error was
	// encountered while processing the incoming message.

	cprintf("Waiting for external messages ...\n");

	remote_command_t rcmd = read_remote_command();

	// Perform quick checks depending on remote command type

	if (rcmd.type == 0 && !is_valid_message_command(rcmd))
		return 2; // return 2 if invalid message was received

	if (rcmd.type == 1)
		return 1; // return 1 if shutdown code was received

	// Grab device with specified device_id.

	device_t* dev = devices[rcmd.device_id];

	// Call device `generate_output_msg` to create message from specified
	// device output port and message fields.

	msg_t* msg = (*dev).generate_output_msg(rcmd.port, rcmd.fields);

	// Grab list of local destination devices.

	dst_list_t *dests = (*dev).getPortDestinations(rcmd.port);

	// Create delivery object.

	delivery_t new_dv = delivery_t(msg, *dests, dev);

	// Add to delivery list.

	dlist.push_back(new_dv);

	// Print log messages and exit successfully.

	cprintf("Created delivery\n");

	cprintf("Received remote delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

	return 0;
}

int send_externals(uint32_t device_id, uint32_t port, msg_t* msg, reg_set_t* regions) {

	// Send an external command (of type 'message') to 'regions'

	int fields[100];

	int result = (*msg).to_arr(fields, 100);

	if (result)
		return result; // return (unsuccessfully) if result is not 0

	reg_set_t::iterator it = (*regions).begin(); // create iterator

	for (; it != (*regions).end(); ++it) {

		printf3("send %d %d %d %d", *it, device_id, port, msg->nscalars);

		for (int i=0; i<msg->nscalars; i++)
			printf3(" %d", fields[i]);

		printf3("\n");
	}

	return 0; // exit successfully

}

void shutdown_externals(reg_set_t other_regions) {

	cprintf("Shutting down external regions\n");

	for (reg_set_t::iterator it = other_regions.begin(); it != other_regions.end(); ++it)
		printf3("send %d -1\n", *it);

}