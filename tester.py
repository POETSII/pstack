import os
import sys
import json

from files import read_file
from parser import parse_poets_xml
from generator import generate_code
from simulator import simulate
from termcolor import colored


def _psim(xml_file):
    xml = read_file(xml_file)
    markup = parse_poets_xml(xml)
    options = {"debug": False, "states": False, "level": 1}
    code, _ = generate_code(markup, options)
    results = simulate(code, quiet=True, use_socat=False, regions=[0])
    return results


def load_functions(py_module_file):
    """Load functions from a module file."""
    parent_dir, file_name = os.path.split(py_module_file)
    import_name = file_name.replace(".py", "")
    sys.path.insert(0, parent_dir)
    module_obj = __import__(import_name)
    functions = []

    for attr in dir(module_obj):
        fun = getattr(module_obj, attr)
        if callable(fun):
            functions.append(fun)

    return functions


def put(str_):
    """Print string with new trailing new line."""
    sys.stdout.write(str_)
    sys.stdout.flush()


def get_checker_doc(checker):
    doc = checker.func_doc
    if not doc:
        return "(unnamed test)"
    return doc[:-1] if doc[-1] == '.' else doc


def get_checker_doc_len(checker):
    return len(get_checker_doc(checker))


def main():

    xml_files = [
        os.path.join("tests", file) for file in os.listdir("tests")
        if file.lower().endswith(".xml")
    ]

    for xml_file in xml_files:

        name, _ = os.path.splitext(xml_file)
        py_file = "%s.py" % name

        cfuncs = sorted(load_functions(py_file), key=get_checker_doc_len)

        pass_str = colored("PASS", "green", attrs=["bold"])
        fail_str = colored("FAIL", "red", attrs=["bold"])

        print("Simulating %s ... " % colored(xml_file, attrs=["bold"]))
        simulation_result = _psim(xml_file)

        for checker in cfuncs:
            put("  - %s ... " % get_checker_doc(checker))
            try:
                checker(simulation_result)
                print pass_str
            except AssertionError:
                print fail_str
                sys.exit(1)


if __name__ == '__main__':
    main()
