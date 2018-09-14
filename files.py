import json

def read_json(file):
    """Read a JSON file."""
    with open(file, "r") as fid:
        return json.load(fid)
