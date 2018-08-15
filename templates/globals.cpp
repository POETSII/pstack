// Global functions

int abort_flag = 0;  // used to exit simulation loop

// Below we define a pointer (active_device) to the device whose handler is
// being executed. This is used to obtain the active device name when
// handler_log and handler_exit are called.

device_t* active_device;

void handler_log(int level, const char *fmt, ...) {

    if (level > {{ options['level'] }})
        return;

    printf("App [%s, %d]: ", active_device->name.c_str(), level);
    va_list va;
    va_start (va, fmt);
    vprintf (fmt, va);
    va_end (va);
    printf("\n");
}

void handler_exit(int exitCode) {

    printf("App [%s, X]: handler_exit(%d) called\n", active_device->name.c_str(), exitCode);
    abort_flag = 1;
}
