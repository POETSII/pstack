// Global functions

int abort_flag = 0;  // used to exit simulation loop
int exit_code = 0;

// Below we define a pointer (active_device) to the device whose handler is
// being executed. This is used to obtain the active device name when
// handler_log and handler_exit are called.

device_t* active_device;

void handler_log(int level, const char *fmt, ...) {

    if (level > {{ options.get('level', 1) }})
        return;

    printf("App [%s, %d]: ", active_device->name.c_str(), level);
    va_list va;
    va_start (va, fmt);
    vprintf (fmt, va);
    va_end (va);
    printf("\n");
}

void handler_exit(int handler_exit_code) {
    printf("App [%s, X]: handler_exit(%d) called\n", active_device->name.c_str(), handler_exit_code);
    exit_code = handler_exit_code;
    abort_flag = 1;
}

void printf3(const char *fmt, ...) {

    // Same as printf but writes to file descriptor 3.

    char buffer[255];
    int len;

    va_list va;
    va_start(va, fmt);
    len = vsprintf(buffer, fmt, va);
    va_end(va);

    write(3, buffer, len);
}
