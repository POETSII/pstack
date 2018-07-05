@ set device_type_map = dict_from_list(graph_type['device_types'], 'id')

@ for group in graph_instance['devices'] | groupby('type')

	@ set devices = group.list
	@ set device_type = group.grouper

	device_t* {{ get_init_function_name(device_type) }}() {

		device_t *devices = new device_t[{{ devices | count}}];

		@ set state_class = get_state_class(device_type)
		@ set props_class = get_props_class(device_type)
		@ set count = group.list | count
		@ set device_type_obj = device_type_map[device_type]
		@ set scalar_props = device_type_obj['properties']['scalars']
		@ set init_msg_t = get_msg_class('__init__')
		@ set init_handler = get_receive_handler_name(device_type, '__init__')

		@ for prop in scalar_props

			@ set property_values = devices | map(attribute='properties') | map(attribute=prop['name']) | list

			{{ prop['type'] }} {{ prop['name'] }} [{{ count }}] = {

				{{- property_values | join(', ') -}}

			};

		@ endfor

		{{ init_msg_t }} *init = new {{ init_msg_t }}();

		for (int i=0; i<{{ devices | count }}; i++) {

			devices[i].state = new {{ state_class }}();

			devices[i].props = new {{ props_class }} (
				{%- for prop in scalar_props %}
					{{- prop['name'] -}} [i]
					{{- ', ' if not loop.last else '' -}}
				{%- endfor -%}
			);

			{{ init_handler }}(devices[i].state, devices[i].props {{ PROP_ARR }}, init);

			printf("Device %d ({{ device_type }}):\n", i);
			{{ state_class }} *ptr = ({{ state_class }}*) devices[i].state;
			(*ptr).print();

		}

		delete init;

		return devices;

	}

@ endfor
