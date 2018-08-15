// vim: set ft=cpp:

#include <set>
#include <vector>
#include <string>
#include <stdio.h>
#include <sys/poll.h>
#include <stdarg.h>

@ include 'globals.cpp'
@ include 'types.cpp'
@ include 'messages.cpp'
@ include 'devices.cpp'
@ include 'shared.cpp'
@ include 'handlers.cpp'
@ include 'init.cpp'
@ include 'edges.cpp'
@ include 'rts.cpp'

int main() {

    std::vector<device_t*> devices;
    std::vector<delivery_t> dlist; // delivery list

    @ set graph_type_class = get_graph_type_props_class(graph_type['id'])

    {{ graph_type_class }} graphProps;

    graphProperties = &graphProps;

    @ set props = graph_type['properties']

    @ for scalar in props['scalars']
        graphProperties->{{ scalar['name'] }} = {{ scalar.get('default') or '0' }};
    @ endfor

    // cprintf("Hello\n"); while (!poll()); read_message();  write_message(); return 0;

    @ set device_types = unique(graph_instance['devices'] | map(attribute='type'))
    @ set init_funcs = pymap(get_init_function_name, device_types | sort)
    @ set init_calls = mformat("%s(devices);", init_funcs) | join("\n")

    cprintf("Initialization:\n---------------\n");

    // Device initialization call must be in the correct order (sorted by
    // device type). This is because elsewhere in the code it is assumed that
    // objects in the vector `devices` correspond to devices in the XML file
    // sorted by key (type, id).

    {{ init_calls }}

    add_edges(devices);

    cprintf("\n");

    // ---- BEGIN RTS SCAN ----

    rts_set_t rts_set;

    for (int i=0; i<devices.size(); i++){

        device_t* dev = devices[i];

        int rts = (*dev).get_rts();

        if (rts) rts_set.insert(dev);

    }

    print_rts_set(rts_set);

    cprintf("\n");

    // ---- END RTS SCAN ----

    for (int i=0; abort_flag == 0; i++) {

        cprintf("Epoch %d:\n--------\n", i+1);

        // ---- BEGIN DELIVERY LIST UPDATE ----

        device_t* dev = select_rts_device(rts_set);

        if (dev == NULL) {

            cprintf("Empty rts set\n");

        } else {

            int port = select_rts_port(dev);

            dst_list_t *dests = (*dev).getPortDestinations(port);

            // Create message by calling send handler

            cprintf("Calling send handler of device <%s> ...\n", dev->name.c_str());

            msg_t* msg = (*dev).send(port);

            // Checking if sender still wants to send (and remove it from
            // rts_set if not)

            int new_rts = (*dev).get_rts();

            if (new_rts == 0) {
                rts_set.erase(dev);
                cprintf("Device <%s> removed from rts_set\n", dev->name.c_str());
            }

            // Create delivery object

            delivery_t new_dv = delivery_t(msg, *dests, dev);

            cprintf("Created new delivery (<%s> message to %d nodes) ...\n", (*msg).getName(), (*dests).size());

            // new_dv.print();

            dlist.push_back(new_dv);

        }

        // ---- END DELIVERY LIST UPDATE ----

        // ---- BEGIN DELIVERY ----

        int pending_deliveries = dlist.size();

        if (pending_deliveries > 0) {

            cprintf("Pending deliveries: %d\n", pending_deliveries);

            // cprintf("Making the delivery:\n");

            delivery_t dv = dlist.at(0);  // Always choose first delivery, for now (TODO)

            // (*dv.msg).print();

            // cprintf("Chosen destination:\n");

            destination_t dst = dv.dst.at(dv.dst.size()-1);  // Always choose last destination, for now (TODO)

            // dst.print();

            // cprintf("Calling receive handler ...\n");

            device_t* dst_dev = (device_t*) dst.device;

            cprintf("Delivering <%s> message from <%s> to <%s>\n", (*dv.msg).getName(), dv.origin->name.c_str(), dst_dev->name.c_str());

            (*dst_dev).receive(dst.port, dv.msg);

            cprintf("Device <%s>: ", dst_dev->name.c_str());

            (*dst_dev).print();

            int dst_dev_rts = (*dst_dev).get_rts();

            if (dst_dev_rts) {

                rts_set.insert(dst_dev);

                print_rts_set(rts_set);
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

            // dv.print();

        } else {

            cprintf("No pending deliveries\n");

        }

        if (dev == NULL && pending_deliveries == 0) {

            printf("End of simulation\n");

            return 0;

        }

        cprintf("\n");

    }

    // ---- END DELIVERY ----

    return 0;
}