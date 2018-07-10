void add_edges(std::vector<device_t*> devices) {

	@ set connections = schema.get_edge_table()
	@ set ncons = connections | count

	int edges[{{ ncons }}][4] = {

		@ for row in connections
			{ {{- row | join(', ') -}} } {{ ',' if not loop.last else '' }}
		@ endfor

	};

	for (int i=0; i<{{ ncons }}; i++) {

		device_t* src_dev = devices[edges[i][0]];
		device_t* dst_dev = devices[edges[i][1]];

		int src_pin = edges[i][2];
		int dst_pin = edges[i][3];

		dst_list_t *dsts = (*src_dev).getPortDestinations(src_pin);

		(*dsts).push_back(destination_t(dst_dev, dst_pin));
	}

	return;

}
