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
    return node.text if node is not None else None


def read_poets_xml(file):
    """Parse POETS xml file."""

    root = load_xml(file)
    graph_type = root.find("./poets:GraphType", namespaces)
    shared_code = graph_type.find("./poets:SharedCode", namespaces)
    device_types = graph_type.find("./poets:DeviceTypes", namespaces)
    message_types = graph_type.find("./poets:MessageTypes", namespaces)
    graph_type_doc = graph_type.find("./poets:Documentation", namespaces)

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
        "scalars": parse_state(msg)
    }


def parse_device_type(root):
    """Parse <DeviceType> POETS xml element."""

    msg = get_child(root, "Message")
    state = get_child(root, "State")

    return {
        "id": root.attrib["id"],
        "state": parse_state(state)
    }


def parse_state(root):
    """Parse a POETS xml element with state fields.

    State fields are <Scalar> or <Array> elements.

    """

    if root is None:
        return []

    scalars = [{
        "name": scalar.attrib['name'],
        "type": scalar.attrib['type']
    } for scalar in root.findall('./poets:Scalar', namespaces)]

    arrays = [{
        "name": array.attrib['name'],
        "type": array.attrib['type'],
        "length": int(array.attrib['length'])
    } for array in root.findall('./poets:Array', namespaces)]

    return {"scalars": scalars, "arrays": arrays}
