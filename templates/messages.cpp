// Message types

@ for message in graph_type['message_types']

    @ set msg_class = get_msg_class(graph_type["id"], message['id'])
    @ set fields = message['fields']

    class {{ msg_class }}: public msg_t {

    public:

        {{ lmap(declare_variable, fields['scalars']) }}

        {{ msg_class }} (){
            this->index = {{ loop.index0 }};
            this->nscalars = {{ fields['scalars'] | count }};
            @ for scalar in fields['scalars']
                this->{{ scalar['name'] }} = 0;
            @ endfor
        }

        {{ msg_class }}(int *arr) {

            int index = 0;

            @ for scalar in fields['scalars']
                this->{{ scalar['name'] }} = ({{ scalar['type'] }}) arr[index++];
            @ endfor

        }

        void print() {
            @ for scalar in fields['scalars']
                cprintf("  - {{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
            @ endfor
        }

        const char* getName() {
            return "{{ message['id'] }}";
        }


        void serialize(char *buf) {

            int index = 0;

            @ for scalar in fields['scalars']

                *(({{ scalar['type'] }}*) (buf + index)) = this->{{ scalar['name'] }};

                index += sizeof({{ scalar['type'] }});

            @ endfor

        }

        int getByteCount() {

            @ set types = fields['scalars'] | map(attribute='type')
            @ set terms = mformat("sizeof(%s)", types) or ["0"]
            return {{ terms | join(' + ') }};

        }

        void deserialize(char *buf) {

            int index = 0;

            @ for scalar in fields['scalars']

                this->{{ scalar['name'] }} = *(({{ scalar['type'] }}*) (buf + index));

                index += sizeof({{ scalar['type'] }});

            @ endfor

        }

        void read_debug() {
            @ for scalar in fields['scalars']
                scanf("%d", &(this->{{ scalar['name']}}));
            @ endfor
        }

        int to_arr(int *arr, int arr_length) {

            // Read (scalar) fields of a message from a given array.

            // The argument `nfields` must equal the class `nscalars` field,
            // otherwise an error is returned.

            if (arr_length < this->nscalars) {
                printf("Function {{ message['id'] }}.to_arr requires array with %d elements (%d provided)\n", this->nscalars, arr_length);
                return 1;
            }

            int index = 0;

            @ for scalar in fields['scalars']
                arr[index++] = this->{{ scalar['name']}};
            @ endfor

            return 0; // exit successfully
        }

    };

@ endfor
