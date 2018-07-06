@ for group in graph_instance['devices'] | groupby('type')

	@ set devices = group.list
	@ set device_type = group.grouper
	@ set device_class = get_device_class(device_type)

	device_t* {{ get_init_function_name(device_type) }}() {

		{{ device_class }} *devices = new {{ device_class }}[{{ devices | count}}];

		@ set state_class = get_state_class(device_type)
		@ set props_class = get_props_class(device_type)
		@ set device_class = get_device_class(device_type)
		@ set count = group.list | count
		@ set device_type_obj = schema.get_device_type(device_type)
		@ set scalar_props = device_type_obj['properties']['scalars']
		@ set init_msg_t = get_msg_class('__init__')
		@ set init_handler = get_receive_handler_name(device_type, '__init__')

		@ for prop in scalar_props

			@ set property_values = devices | map(attribute='properties') | map(attribute=prop['name']) | list

			{{ prop['type'] }} {{ prop['name'] }} [{{ count }}] = {

				{{- property_values | join(', ') -}}

			};

		@ endfor

		for (int i=0; i<{{ devices | count }}; i++) {

			devices[i].setProperties(
				{%- for prop in scalar_props %}
					{{- prop['name'] -}} [i]
					{{- ', ' if not loop.last else '' -}}
				{%- endfor -%}
			);

			devices[i].init();

			printf("Device %d ({{ device_type }}):\n", i);
			{{ state_class }} *ptr = ({{ state_class }}*) devices[i].state;
			(*ptr).print();

		}

		return (device_t*) devices;

	}

@ endfor
