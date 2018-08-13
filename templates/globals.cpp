// Global functions

#include <stdarg.h>

void handler_log(int level, const char *fmt, ...) {
    cprintf("App: ");
    va_list va;
    va_start (va, fmt);
    cprintf (fmt, va);
    va_end (va);
    cprintf("\n");
}

void handler_exit(int exitCode) {

	cprintf("App: handler_exit(%d) called\n", exitCode);
}

// graphProperties object

@ set graph_type_class = get_graph_type_props_class(graph_type['id'])

{{ graph_type_class }} *graphProperties;
