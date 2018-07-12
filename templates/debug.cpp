bool poll() {

    // Return true iff input is available on stdin.

    struct pollfd fds;
    int ret;
    fds.fd = 0; /* this is STDIN */
    fds.events = POLLIN;
    ret = poll(&fds, 1, 0);
    return (ret == 1);
}

void read_message() {

    char buff[80];

    gets(buff);

    printf("Finished reading messsage.\n");

    ack_msg_t msg;

    msg.deserialize(buff);

    msg.print();

}

void test_serialization() {

    ack_msg_t msg;
    ack_msg_t reply;

    msg.src = 2;
    msg.dst = 3;
    msg.discovered = 4;
    msg.callback = 5;

    char buf[24];

    msg.serialize(buf);

    int bytes = msg.getByteCount();

    for (int i=0; i<bytes; i++)
        printf("buf[%2d] = 0x%x\n", i, buf[i]);

    reply.deserialize(buf);

    reply.print();
}

