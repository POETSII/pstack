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

    ping_msg_t msg;

    msg.deserialize(buff);

    msg.print();

}

void write_message() {

    char buff[80];

    ping_msg_t msg;

    msg.src = 2;
    msg.dst = 3;

    msg.serialize(buff);

    printf("msg: ");

    int bytes = msg.getByteCount();

    for (int i=0; i<bytes; i++)
        printf("%c", buff[i]);

    printf("\n");

}
