// vim: set ft=cpp:

#include <set>
#include <vector>
#include <set>
#include <string>
#include <stdio.h>
#include <sys/poll.h>
#include <stdarg.h>
#include <unistd.h>

@ include 'types.cpp'
@ include 'globals.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'
@ include 'graph.cpp'
@ include 'shared.cpp'
@ include 'handlers.cpp'
@ include 'init.cpp'
@ include 'edges.cpp'
@ include 'rts.cpp'
@ include 'externals.cpp'

int main(int argc, char *argv[]) {

    std::vector<device_t*> devices;
    std::vector<delivery_t> dlist; // delivery list

    @ set graph_type_class = get_graph_type_props_class(graph_type['id'])

    {{ graph_type_class }} graphProps;

    graphProperties = &graphProps;

    @ set props = graph_type['properties']

    @ for scalar in props['scalars']
        graphProperties->{{ scalar['name'] }} = {{ scalar.get('default') or '0' }};
    @ endfor

    @ set device_types = unique(graph_instance['devices'] | map(attribute='type'))
    @ set init_funcs = pymap(get_init_function_name, device_types | sort)
    @ set init_calls = mformat("local_devices += %s(devices, simulation_region);", init_funcs) | join("\n")

    cprintf("Initialization:\n---------------\n");

    const uint32_t simulation_region = (argc > 1) ? std::stoi(argv[1]) : 0;
    const uint32_t pid = (argc > 2) ? std::stoi(argv[2]) : 0;

    reg_set_t other_regions;

    @ for region in schema.get_regions()
        if (simulation_region != {{ region }})
            other_regions.insert({{ region }});
    @ endfor

    const bool exist_other_regions = !other_regions.empty();

    // Device initialization call must be in the correct order (sorted by
    // device type). This is because elsewhere in the code it is assumed that
    // objects in the vector `devices` correspond to devices in the XML file
    // sorted by key (type, id).

    int local_devices = 0;

    {{ init_calls }}

    if (local_devices == 0) {
        printf("There are no local devices in region %d\n", simulation_region);
        return 1;
    }

    add_edges(devices, simulation_region);

    cprintf("\n");

    // ---- BEGIN RTS SCAN ----

    int delivered_messages = 0;

    rts_set_t rts_set;

    for (int i=0; i<devices.size(); i++){

        device_t* dev = devices[i];

        if (dev->region != simulation_region)
            continue;  // skip devices in external regions

        int rts = (*dev).get_rts();

        if (rts) rts_set.insert(dev);

    }

    print_rts_set(rts_set);

    cprintf("\n");

    // ---- END RTS SCAN ----

    int i;

    for (i=0; abort_flag == 0; i++) {

        cprintf("Epoch %d:\n--------\n", i+1);

        // ---- BEGIN DELIVERY LIST UPDATE ----

        device_t* dev = select_rts_device(rts_set);

        bool is_rts_set_empty = dev == NULL;

        active_device = dev;

        if (is_rts_set_empty) {

            cprintf("Empty rts set\n");

        } else {

            int port = select_rts_port(dev);

            if (port == -1) {

                // Could not determine output port, either because (1) rts is
                // no longer asserted, (2) rts value is incorrect.

                int current_rts = (*dev).get_rts();

                if (current_rts == 0)
                    printf("Error, RTS of device <%s> was de-asserted before calling send handler.\n", dev->name.c_str());
                else
                    printf("Error, RTS handler of device <%s> returned invalid value (%d)\n", dev->name.c_str(), current_rts);

                return 1;
            }

            dst_list_t *dests = (*dev).getPortDestinations(port);
            reg_set_t *regs = (*dev).getPortOutputRegions(port);

            // Create message by calling send handler

            cprintf("Calling send handler of device <%s> ...\n", dev->name.c_str());

            msg_t* msg = (*dev).send(port);

            // Check if sender still wants to send (and remove it from rts_set
            // if not)

            int new_rts = (*dev).get_rts();

            if (new_rts == 0) {
                rts_set.erase(dev);
                cprintf("Device <%s> removed from rts_set\n", dev->name.c_str());
            }

            // Create delivery object

            if ((*dests).size() > 0) {

                delivery_t new_dv = delivery_t(msg, *dests, dev);

                cprintf("Created local delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

                dlist.push_back(new_dv);

            }

            if ((*regs).size() > 0) {

                cprintf("Created remote delivery to %d external regions.\n", (*regs).size());

                remote_command_t rcmd;

                rcmd.type = MSG;
                rcmd.device_id = dev->index;
                rcmd.port = port;
                rcmd.nfields = msg->nscalars;

                int result = (*msg).to_arr(rcmd.fields, MAX_REMOTE_MSG_FIELDS);

                if (result) {
                    printf("Encountered error while sending to external regions, aborting simulation.\n");
                    break;
                }

                result = write_remote_command_multi(rcmd, pid, regs);

                if (result) {
                    printf("Encountered error while sending to external regions, aborting simulation.\n");
                    break;
                }

                cprintf("Sent remote delivery command(s).\n");

            }

        }

        // ---- END DELIVERY LIST UPDATE ----

        // ---- BEGIN DELIVERY ----

        int pending_deliveries = dlist.size();

        if (pending_deliveries > 0) {

            cprintf("Pending deliveries: %d\n", pending_deliveries);

            delivery_t dv = dlist.at(0);  // Always choose first delivery, for now (TODO)

            destination_t dst = dv.dst.at(dv.dst.size()-1);  // Always choose last destination, for now (TODO)

            device_t* dst_dev = (device_t*) dst.device;

            active_device = dst_dev;

            cprintf("Delivering <%s> message from <%s> to <%s>\n", (*dv.msg).getName(), dv.origin->name.c_str(), dst_dev->name.c_str());

            if (dst_dev->region == simulation_region) {

                // Destination device is in simulation region.

                // Call receive handler then scan device for rts change.

                (*dst_dev).receive(dst.port, dv.msg);

                delivered_messages++;

                cprintf("Device <%s>: ", dst_dev->name.c_str());

                (*dst_dev).print();

                int dst_dev_rts = (*dst_dev).get_rts();

                if (dst_dev_rts) {

                    rts_set.insert(dst_dev);

                    print_rts_set(rts_set);
                }

            } else {

                // Destination device is outside simulation region.

                cprintf("error\n");

                // send_externals(dst, dv);

            }

            // cprintf("Removing device <%s> from delivery object destinations ...\n", dst_dev->name.c_str());

            dv.dst.pop_back();

            if (dv.dst.size() == 0) {

                cprintf("Delivery is complete, removing from dlist ...\n");

                // Remove by swapping with last element then doing pop_back()

                delivery_t last_delivery = dlist.at(dlist.size() - 1);

                dlist[0] = last_delivery;

                dlist.pop_back();

            } else {

                cprintf("Remaining destinations in this delivery: ");

                dv.print_destinations();

                dlist[0] = dv; // put modified delivery object in dlist

            }

        } else {

            cprintf("No pending deliveries\n");

            if (is_rts_set_empty) {

                // There no pending deliveries and no devices wishing to send.

                // At this point, wait for external messages (if there are
                // external regions) or end the simulation otherwise.

                if (exist_other_regions) {

                    // Wait for external commands.

                    remote_command_t rcmd = read_remote_command(pid, simulation_region);

                    if (!rcmd._wellformed) {
                        printf("Received malformed remote command\n");
                        break;
                    }

                    if (rcmd.type == MSG && !is_valid_message_command(rcmd)) {
                        printf("Received malformed remote command (of message type)\n");
                        break;
                    }

                    if (rcmd.type == SHUTDOWN) {
                        printf("Received external shutdown command\n");
                        break;
                    }

                    device_t* dev = devices[rcmd.device_id];

                    // Call device `generate_output_msg` to create message from specified
                    // device output port and message fields.

                    msg_t* msg = (*dev).generate_output_msg(rcmd.port, rcmd.fields);

                    // Grab list of local destination devices.

                    dst_list_t *dests = (*dev).getPortDestinations(rcmd.port);

                    // Create delivery object.

                    delivery_t new_dv = delivery_t(msg, *dests, dev);

                    // Add to delivery list.

                    dlist.push_back(new_dv);

                    // Print log messages and exit successfully.

                    cprintf("Created delivery\n");

                    cprintf("Received remote delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

                } else {

                    // Nothing else to do, end the simulation.

                    printf("End of simulation\n");
                    break;
                }
            }

        }

        cprintf("\n");

    }

    // If the simulation was aborted and is part of a distributed simulation
    // then send shutdown signal to other parts.

    if (abort_flag && exist_other_regions) {

        cprintf("Shutting down external regions\n");

        remote_command_t rcmd;
        rcmd.type = SHUTDOWN;

        int result = write_remote_command_multi(rcmd, pid, &other_regions);

        if (result)
            printf("Encountered error while sending shutdown signal to external regions.\n");
    }

    // Print simulation metrics and device states.

    printf("Metric [Delivered messages]: %d\n", delivered_messages);
    printf("Metric [Exit code]: %d\n", exit_code);

    print_debug = 1;

    for (int i=0; i<devices.size(); i++) {
        device_t* dev = devices[i];

        if (dev->region != simulation_region)
            continue;

        printf("State [%s]: ", dev->name.c_str());
        (*dev).print();
    }

    return 0;
}