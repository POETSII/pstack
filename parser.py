#!/usr/bin/env python

import re
import json
import docopt

import xml.etree.ElementTree as ET

namespaces = {
    "poets": "https://poets-project.org/schemas/virtual-graph-schema-v2"
}

usage="""POETS Markup Parser v0.1

Usage:
  parser.py <app.xml>

"""


def load_xml(xml):
    """Parse an XML string."""
    try:
        return ET.ElementTree(ET.fromstring(xml)).getroot()
    except IOError:
        raise Exception("File not found: %s" % xml_file)


def get_children(parent, child_name):
    """Return children of 'parent' with a given name."""
    return parent.findall("poets:%s" % child_name, namespaces)


def get_child(parent, child_name):
    """Return child of 'parent' with a given name."""
    return parent.find("poets:%s" % child_name, namespaces)


def get_text(element):
    """Return inner text of an XML element."""

    if element is None:
        return None

    if element.text is None:
        return None

    return element.text.strip()


def parse_poets_xml(xml):
    """Parse POETS xml file."""

    root = load_xml(xml)

    graph_type = get_child(root, "GraphType")
    graph_inst = get_child(root, "GraphInstance")

    return {
        "graph_type": parse_graph_type(graph_type),
        "graph_instance": parse_graph_instance(graph_inst)
    }


def parse_graph_type(graph_type):
    """Parse a <GraphType> element."""

    properties = get_child(graph_type, "Properties")
    shared_code = get_child(graph_type, "SharedCode")
    device_types = get_child(graph_type, "DeviceTypes")
    message_types = get_child(graph_type, "MessageTypes")
    graph_type_doc = get_child(graph_type, "Documentation")

    return {
        "id": graph_type.attrib['id'],
        "doc": get_text(graph_type_doc),
        "shared_code": get_text(shared_code),
        "device_types": map(parse_device_type, device_types),
        "message_types": map(parse_message_type, message_types),
        "properties": parse_state(properties)
    }


def parse_graph_instance(graph_inst):
    """Parse a <GraphInstance> element."""

    devices = [
        {
            "id": device.attrib["id"],
            "type": device.attrib["type"],
            "properties": parse_property_str(get_text(get_child(device, "P")))
        }
        for device in get_child(graph_inst, "DeviceInstances")
    ]

    edges = [
        parse_edge_str(edge.attrib["path"])
        for edge in get_child(graph_inst, "EdgeInstances")
    ]

    return {"devices": devices, "edges": edges}


def parse_edge_str(edge_str):
    """Parse a POETS edge string.

    POETS Edge strings represent connections between devices are in the
    following format:

    dev1:pin1-dev2:pin2

    What may be slightly confusing is that this represents a directional
    connection from dev2 to dev1 (not the other way around).

    In the example above, pin2 of dev2 (an output pin) is connected to pin1 of
    dev1 (an input pin).
    """

    reg1 = r"(\w+)\:(\w+)\-(\w+)\:(\w+)"
    pat1 = re.compile(reg1, flags=re.MULTILINE)

    for item in pat1.findall(edge_str):
        return {
            "dst": item[:2],
            "src": item[2:]
        }


def parse_property_str(prop_str):
    """Parse a POETS property string.

    Property strings (in POETS) are string representations of JSON
    dictionaries, without the leading and trailing brackets.
    """
    return json.loads("{%s}" % prop_str) if prop_str else {}


def parse_message_type(root):
    """Parse a <MessageType> element."""

    doc = get_child(root, "Documentation")
    msg = get_child(root, "Message")

    return {
        "id": root.attrib["id"],
        "doc": get_text(doc),
        "fields": parse_state(msg)
    }


def parse_device_type(root):
    """Parse a <DeviceType> element."""

    msg = get_child(root, "Message")
    state = get_child(root, "State")
    props = get_child(root, "Properties")

    input_pins = [
        {
            "name": pin.attrib["name"],
            "message_type": pin.attrib["messageTypeId"],
            "on_receive": get_text(get_child(pin, "OnReceive"))
        }
        for pin in get_children(root, "InputPin")
    ]

    output_pins = [
        {
            "name": pin.attrib["name"],
            "message_type": pin.attrib["messageTypeId"],
            "on_send": get_text(get_child(pin, "OnSend"))
        }
        for pin in get_children(root, "OutputPin")
    ]

    return {
        "id": root.attrib["id"],
        "state": parse_state(state),
        "properties": parse_state(props),
        "ready_to_send": get_text(get_child(root, "ReadyToSend")),
        "input_pins": input_pins,
        "output_pins": output_pins
    }


def parse_state(root):
    """Parse an xml element with state fields.

    State fields are <Scalar> or <Array> elements.

    There are currently several elements in the POETS schema that contain state
    fields, including:

    - <State> of <DeviceType>
    - <Message> of <MessageType>
    - <Properties> of <DeviceType>
    - <Properties> of <GraphType>

    """

    if root is None:
        return []

    scalars = [{
        "name": scalar.attrib['name'],
        "type": scalar.attrib['type'],
        "doc": get_text(get_child(scalar, "Documentation")),
        "default": scalar.attrib.get('default'),
    } for scalar in get_children(root, "Scalar")]

    arrays = [{
        "name": array.attrib['name'],
        "type": array.attrib['type'],
        "doc": get_text(get_child(array, "Documentation")),
        "length": int(array.attrib['length'])
    } for array in get_children(root, "Array")]

    return {"scalars": scalars, "arrays": arrays}


def main():
    args = docopt.docopt(usage, version="v0.1")
    markup = read_poets_xml(args["<app.xml>"])
    print json.dumps(markup, indent=4)


if __name__ == '__main__':
    main()
