enum rtype {MSG = 0, SHUTDOWN = 1};

#define MAX_REMOTE_MSG_FIELDS 100

struct remote_command_t {
	rtype type;                         // command type: (0) message, (1) shutdown
	int region;			                // intended destination region
	int device_id;                      // remote device id
	int port;                           // output port of remote device
	int nfields;                        // number of field items
	int fields[MAX_REMOTE_MSG_FIELDS];  // message fields
	bool _wellformed;                   // message is well-formed (computed field)
};

int comp_arr(char *a1, const char *a2, int n) {

	// Compare arrays.

	// Return 0 iff arrays a1 and a2 are identical up to n elements, 1
	// otherwise.

	for (int i=0; i<n; i++)
		if (a1[i] != a2[i])
			return 1;

	return 0;
}

remote_command_t read_remote_command() {

	// Read remote command from stdin.

	remote_command_t rcmd;

	int nfields;
	char prefix[256];

	cprintf("Waiting for external commands ...\n");

	// Check if command has "send" prefix

	scanf("%s", prefix);

	if (comp_arr(prefix, "send", 4)) {
		rcmd._wellformed = false;
		return rcmd;
	}

	scanf("%d %d", &rcmd.type, &rcmd.region);

	if (rcmd.type == MSG) {

		scanf("%d %d %d", &(rcmd.device_id), &(rcmd.port), &(rcmd.nfields));

		for (int i=0; i<rcmd.nfields; i++)
			scanf("%d", rcmd.fields + i);

	}

	rcmd._wellformed = true;

	return rcmd;

}

void print_remote_command(remote_command_t rcmd) {

	// Print content of remote command (for debugging).

	printf("Remote command:\n");

	printf("  - type: %d\n", rcmd.type);
	printf("  - region: %d\n", rcmd.region);

	if (rcmd.type == MSG) {

		printf("  - device_id: %d\n", rcmd.device_id);
		printf("  - port: %d\n", rcmd.port);
		printf("  - fields (n = %d):\n", rcmd.nfields);

		for (int i=0; i<rcmd.nfields; i++)
			printf("    - [%d] = %d\n", i, rcmd.fields[i]);
	}

}

bool is_valid_message_command(remote_command_t rcmd) {

	// Validate (message-type) remote command.

	const int ndevices = {{ graph_instance['devices'] | count }};
	const int nmsgtypes = {{ graph_type['message_types'] | count }};

	if (rcmd.type != MSG) {
		printf("External command does not contain message\n");
		return false; // not message command
	}

	if (rcmd.device_id<0 || rcmd.device_id>=ndevices) {
		printf("External message command contains incorrect device id (%d)\n", rcmd.device_id);
		return false; // invalid device id
	}

	return true;

}

int read_message_from_externals(
	std::vector<device_t*> &devices,
	std::vector<delivery_t> &dlist,
	uint32_t simulation_region) {

	// Receive external command.

	// Return 0 if successful, 1 if shutdown signal was received or error was
	// encountered while processing the incoming message.

	remote_command_t rcmd = read_remote_command();

	// Run quick checks on command content

	if (!rcmd._wellformed)
		return 2;

	if (rcmd.type == MSG && !is_valid_message_command(rcmd))
		return 2; // return 2 if invalid message was received

	if (rcmd.type == SHUTDOWN)
		return 1; // return 1 if shutdown code was received

	if (rcmd.region != simulation_region) {
		printf("Received external command intended for another region (%d)\n", rcmd.region);
		return 2;
	}

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

void write_remote_command(remote_command_t rcmd, int region) {

	printf3("send %d %d", rcmd.type, region);

	if (rcmd.type == MSG) {

		printf3(" %d %d %d", rcmd.device_id, rcmd.port, rcmd.nfields);

		for (int i = 0; i < rcmd.nfields; i++)
			printf3(" %d", rcmd.fields[i]);

	}

	printf3("\n");

}

void write_remote_command_multi(remote_command_t rcmd, reg_set_t* regions) {

	// Send remote command to multiple regions.

	reg_set_t::iterator it = (*regions).begin(); // create iterator

	for (; it != (*regions).end(); ++it) {
		rcmd.region = *it;
		write_remote_command(rcmd, *it);
	}

}

int write_message_to_externals(
	uint32_t device_id,
	uint32_t port,
	msg_t* msg,
	reg_set_t* regions) {

	remote_command_t rcmd;

	rcmd.type = MSG;
	rcmd.device_id = device_id;
	rcmd.port = port;
	rcmd.nfields = msg->nscalars;

	int result = (*msg).to_arr(rcmd.fields, MAX_REMOTE_MSG_FIELDS);

	if (result) return result; // return (unsuccessfully)

	write_remote_command_multi(rcmd, regions);

	return 0; // exit successfully
}

void shutdown_externals(reg_set_t* other_regions) {

	remote_command_t rcmd;
	rcmd.type = SHUTDOWN;

	cprintf("Shutting down external regions\n");

	write_remote_command_multi(rcmd, other_regions);
}