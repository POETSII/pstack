// Global functions

int abort_flag = 0;  // used to exit simulation loop

void handler_log(int level, const char *fmt, ...) {

    if (level > 1)
        return;

    printf("App [%d]: ", level);
    va_list va;
    va_start (va, fmt);
    vprintf (fmt, va);
    va_end (va);
    printf("\n");
}

void handler_exit(int exitCode) {

    printf("App [X]: handler_exit(%d) called\n", exitCode);
    abort_flag = 1;
}

// cprintf (conditional printf):

// This is a simple macro that either wraps printf (when --debug is supplied)
// or does nothing.

#if {{ '1' if options['debug'] else '0' }}
    #define cprintf(...) printf(__VA_ARGS__)
#else
    #define cprintf(...) (__VA_ARGS__);
#endif
