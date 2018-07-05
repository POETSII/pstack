@ for group in graph_instance['devices'] | groupby('type')

@ set devices = group.list
@ set device_type = group.grouper

	device_t* {{ get_init_function_name(device_type) }}() {

		@ set devices = graph_instance['devices']

		device_t *devices = new device_t[{{ devices | count}}];

		@ set STATE_CLASS_NAME = get_state_class(device_type)
		@ set PROPS_CLASS_NAME = get_prop_class(device_type)
		@ set count = group.list | count
		@ set device_type_obj = graph_type['device_types'] | selectattr('id', 'equalto', device_type) | first
		@ set scalar_props = device_type_obj['properties']['scalars']
		@ set INIT_MSG_T = get_msg_class('__init__')
		@ set INIT_HANDLER = get_receive_handler_name(device_type, '__init__')

		@ for prop in scalar_props

			{{ prop['type'] }} {{ prop['name'] }} [{{ count }}] = {

				{{- devices | map(attribute='properties') | map(attribute=prop['name']) | list | join(', ') -}}

			};

		@ endfor

		{{ INIT_MSG_T }} *init = new {{ INIT_MSG_T }}();

		for (int i=0; i<{{ devices | count }}; i++) {
			devices[i].state = new node_state_t();
			devices[i].props = new node_props_t(
				{%- for prop in scalar_props %}
					{{- prop['name'] -}} [i]
					{{- ', ' if not loop.last else '' -}}
				{%- endfor -%}
			);
			{{ INIT_HANDLER }}(devices[i].state, devices[i].props {{ PROP_ARR }}, init);
			printf("Device %d:\n", i);
			{{ STATE_CLASS_NAME }} *ptr = ({{ STATE_CLASS_NAME }}*) devices[i].state;
			(*ptr).print();

		}

		delete init;

		return devices;

	}

@ endfor
