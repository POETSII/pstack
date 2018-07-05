// Message types

@ for message in graph_type['message_types']

    @ set msg_class = get_msg_class(message['id'])
    @ set fields = message['fields']

    class {{ msg_class }}: public msg_t {

    public:

        {{ lmap(declare_variable, fields['scalars']) }}

        {{ msg_class }} (){
            @ for scalar in fields['scalars']
                this->{{ scalar['name'] }} = 0;
            @ endfor
        }

        void print() {
            @ for scalar in fields['scalars']
                printf("  - {{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
            @ endfor
        }
    };

@ endfor
