// Message types

@ for message in graph_type['message_types']
@ set CLASS_NAME = get_msg_class(message['id'])
class {{ CLASS_NAME }}: public msg_t {

public:

    @ for scalar in message['fields']['scalars']
    {{- scalar['type'] }} {{ scalar['name'] }};
    @ endfor

    {{ CLASS_NAME }} (){
    @ for scalar in message['fields']['scalars']
        this->{{ scalar['name'] }} = 0;
    @ endfor
    }

    void print() {
    @ for scalar in message['fields']['scalars']
        printf("  - {{ scalar['name']}} = %d\n", this->{{ scalar['name']}});
    @ endfor
    }
};

@ endfor
