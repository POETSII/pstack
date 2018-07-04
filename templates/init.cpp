device_t* initialize_devices() {

	@ set devices = graph_instance['devices']

	device_t *devices = new device_t[{{ devices | count}}];

	@ set device_counter = 0

	@ for group in devices | groupby('type')

		@ set device_type = group.grouper
		@ set group_devices = group.list
		@ set STATE_CLASS_NAME = get_state_class(device_type)
		@ set PROPS_CLASS_NAME = get_prop_class(device_type)
		@ set count = group.list | count

		// Properties of '{{ device_type }}' devices:

		@ for device in group_devices

			@ set properties = device['properties']
			@ set device_index = device_counter + loop.index0

			// ---

			devices[{{ device_index }}].state = new {{ STATE_CLASS_NAME }}();

			devices[{{ device_index }}].props = new {{ PROPS_CLASS_NAME }}(
				{{- properties.values() | join(', ') -}}
			);

		@ endfor

			// ---

		// Initialize states of '{{ device_type }}' devices:

		@ set INIT_MSG_T = get_msg_class('__init__')
		@ set INIT_HANDLER = get_receive_handler_name(device_type, '__init__')

		{{ INIT_MSG_T }} *init = new {{ INIT_MSG_T }}();

		for (int i={{ device_counter }}; i<{{ device_counter + count }}; i++) {
			{{ INIT_HANDLER }}(devices[i].state, devices[i].props {{ PROP_ARR }}, init);
			// node_state_t *ptr2 = (node_state_t*) (devices + i);
			// printf("  + %d\n", ptr2->distance);
			printf("Device %d:\n", i);
			{{ STATE_CLASS_NAME }} *ptr = ({{ STATE_CLASS_NAME }}*) devices[i].state;
			(*ptr).print();
		}

		delete init;

		@ set device_counter = device_counter + count

	@ endfor

	return devices;

}