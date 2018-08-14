@ for group in graph_instance['devices'] | groupby('type')

	@ set devices = group.list
	@ set device_type = group.grouper
	@ set device_class = get_device_class(device_type)

	void {{ get_init_function_name(device_type) }}(std::vector<device_t*> &devices) {

		// {{ device_class }} *devices = new {{ device_class }}[{{ devices | count}}];

		@ set state_class = get_state_class(graph_type["id"], device_type)
		@ set props_class = get_props_class(graph_type["id"], device_type)
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

		@ set device_names = devices | map(attribute="id")
		@ set device_names_str = mformat('"%s"', device_names) | join(', ')

		const std::string names[] = { {{ device_names_str }} };

		for (int i=0; i<{{ devices | count }}; i++) {

			{{ device_class }} *new_device = new {{ device_class }};

			new_device->name = names[i];

			(*new_device).setProperties(
				{%- for prop in scalar_props %}
					{{- prop['name'] -}} [i]
					{{- ', ' if not loop.last else '' -}}
				{%- endfor -%}
			);

			(*new_device).init();

			cprintf("Device <%s> ({{ device_type }}): ", new_device->name.c_str());

			(*new_device).print();

			devices.push_back((device_t*) new_device);

		}

	}

@ endfor
