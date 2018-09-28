enum rtype {MSG = 0, SHUTDOWN = 1};

#define MAX_REMOTE_MSG_FIELDS 100

struct remote_command_t {
    rtype type;                         // command type: (0) message, (1) shutdown
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

remote_command_t read_remote_command(uint32_t simulation_region) {

    // Read remote command from stdin.

    remote_command_t rcmd;

    int nfields;
    char temp[256];

    printf3("blpop %d 0\n", simulation_region);

    cprintf("Waiting for external commands ...\n");

    scanf("%s", temp); // reads "*2"
    scanf("%s", temp); // reads "$N"
    scanf("%s", temp); // read queue name
    scanf("%s", temp); // read "$M"

    // Now read external message

    int rcmd_type;
    scanf("%d", &rcmd_type);
    rcmd.type = (rtype) rcmd_type;

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

int write_remote_command(remote_command_t rcmd, int region) {

    // Push a remote command to a Redis queue.

    // Return 0 iff successful.

    printf3("rpush %d \"%d", region, rcmd.type);

    if (rcmd.type == MSG) {

        printf3(" %d %d %d", rcmd.device_id, rcmd.port, rcmd.nfields);

        for (int i = 0; i < rcmd.nfields; i++)
            printf3(" %d", rcmd.fields[i]);

    }

    printf3("\"\n");

    // Read Redis response

    // This should be in the form ":INTEGER" where INTEGER is the current
    // length of the pushed-to Redis queue.

    char response[256];
    scanf("%s", response);
    return response[0] == ':' ? 0 : 1;
}

int write_remote_command_multi(remote_command_t rcmd, reg_set_t* regions) {

    // Send remote command to multiple regions.

    reg_set_t::iterator it = (*regions).begin(); // create iterator

    for (; it != (*regions).end(); ++it) {
        int result = write_remote_command(rcmd, *it);
        if (result) return result; // bubble up error
    }

    return 0; // return (successfully)
}
