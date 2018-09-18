@ for group in graph_instance['devices'] | groupby('type')

	@ set devices = group.list | sort(attribute='id')
	@ set device_type = group.grouper
	@ set device_class = get_device_class(device_type)

	int {{ get_init_function_name(device_type) }}(std::vector<device_t*> &devices, uint32_t simulation_region) {

		@ set state_class = get_state_class(graph_type["id"], device_type)
		@ set props_class = get_props_class(graph_type["id"], device_type)
		@ set device_class = get_device_class(device_type)
		@ set count = group.list | count
		@ set device_type_obj = schema.get_device_type(device_type)
		@ set scalar_props = device_type_obj['properties']['scalars']
		@ set init_msg_t = get_msg_class(graph_type["id"], '__init__')
		@ set init_handler = get_receive_handler_name(device_type, '__init__')

		@ for prop in scalar_props
			@ set property_values = devices | map(attribute='properties') | map(attribute=prop['name']) | list
			{{ prop['type'] }} {{ prop['name'] }} [{{ count }}] = {
				{{- property_values | join(', ') -}}
			};
		@ endfor

		@ set device_names = devices | map(attribute="id") | list
		@ set device_names_str = mformat('"%s"', device_names) | join(', ')
		@ set device_regions = schema.get_device_regions(devices)
		@ set scalar_prop_names = scalar_props | map(attribute='name') | list
		@ set scalar_prop_names_ith = mformat('%s[i]', scalar_prop_names)

		const std::string names[] = { {{ device_names_str }} };
		const uint32_t regions[] = { {{ device_regions | join(', ') }} };

		int local_devices = 0;

		for (int i=0; i<{{ devices | count }}; i++) {

			{{ device_class }} *new_device = new {{ device_class }};

			new_device->name = names[i];

			(*new_device).setProperties(
				{{- scalar_prop_names_ith | join(', ') -}}
			);

			new_device->index = devices.size();
			new_device->region = regions[i];

			active_device = new_device;

			// Only initialize devices within simulation region ...

			if (regions[i] == simulation_region) {
				(*new_device).init();
				local_devices++;
				cprintf("Device <%s> ({{ device_type }}): ", new_device->name.c_str());
				(*new_device).print();
			}

			devices.push_back((device_t*) new_device);

		}

		return local_devices;

	}

@ endfor
