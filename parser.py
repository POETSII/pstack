import xml.etree.ElementTree as ET

namespaces = {
    "poets": "https://poets-project.org/schemas/virtual-graph-schema-v2"
}


def load_xml(file):
    """Parse xml file."""
    try:
        return ET.parse(file).getroot()
    except IOError:
        raise Exception("File not found: %s" % file)


def get_children(parent, child_name):
    """Return children of 'parent' with name 'child_name'."""
    return parent.findall("poets:%s" % child_name, namespaces)


def get_child(parent, child_name):
    """Return child of 'parent' with name 'child_name'."""
    return parent.find("poets:%s" % child_name, namespaces)


def get_node_text(node):
    return node.text.strip() if node is not None else None


def read_poets_xml(file):
    """Parse POETS xml file."""

    root = load_xml(file)
    graph_type = get_child(root, "GraphType")
    shared_code = get_child(graph_type, "SharedCode")
    device_types = get_child(graph_type, "DeviceTypes")
    message_types = get_child(graph_type, "MessageTypes")
    graph_type_doc = get_child(graph_type, "Documentation")

    return {
        "graph_type": {
            "id": graph_type.attrib['id'],
            "doc": get_node_text(graph_type_doc),
            "shared_code": get_node_text(shared_code),
            "device_types": map(parse_device_type, device_types),
            "message_types": map(parse_message_type, message_types)
        }
    }

    return graph_type


def parse_message_type(root):
    """Parse <MessageType> POETS xml element."""

    doc = get_child(root, "Documentation")
    msg = get_child(root, "Message")

    return {
        "id": root.attrib["id"],
        "doc": get_node_text(doc),
        "fields": parse_state(msg)
    }


def parse_device_type(root):
    """Parse <DeviceType> POETS xml element."""

    msg = get_child(root, "Message")
    state = get_child(root, "State")

    return {
        "id": root.attrib["id"],
        "state": parse_state(state),
        "ready_to_send": get_child(root, "ReadyToSend").text.strip()

    }


def parse_state(root):
    """Parse a POETS xml element with state fields.

    State fields are <Scalar> or <Array> elements.

    """

    if root is None:
        return []

    scalars = [{
        "name": scalar.attrib['name'],
        "type": scalar.attrib['type'],
        "doc": get_node_text(get_child(scalar, "Documentation")),
    } for scalar in get_children(root, "Scalar")]

    arrays = [{
        "name": array.attrib['name'],
        "type": array.attrib['type'],
        "doc": get_node_text(get_child(scalar, "Documentation")),
        "length": int(array.attrib['length'])
    } for array in get_children(root, "Array")]

    return {"scalars": scalars, "arrays": arrays}
