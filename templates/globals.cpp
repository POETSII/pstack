// Global functions

#include <stdarg.h>

void handler_log(int level, const char *fmt, ...) {

    printf("App: ");
    va_list va;
    va_start (va, fmt);
    vprintf (fmt, va);
    va_end (va);
    printf("\n");
}

void handler_exit(int exitCode) {

	printf("App: handler_exit(%d) called\n", exitCode);
}

// graphProperties object

@ set graph_type_class = get_graph_type_props_class(graph_type['id'])

{{ graph_type_class }} *graphProperties;
