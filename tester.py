import os
import sys
import json

from psim import psim
from files import read_file
from termcolor import colored


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


def run_tests(sim_result, py_file, verbose=True):

    cfuncs = sorted(load_functions(py_file), key=get_checker_doc_len)

    pass_str = colored("PASS", "green", attrs=["bold"])
    fail_str = colored("FAIL", "red", attrs=["bold"])

    def cprint(text):
        if verbose:
            print text

    for checker in cfuncs:
        if verbose:
            put("  - %s ... " % get_checker_doc(checker))
        try:
            checker(sim_result)
            cprint(pass_str)
        except Exception:
            cprint(fail_str)
            return False

    return True


def get_files():
    """Return list of (xml, py) file tuples in tests dir."""
    xml_files = [
        os.path.join("tests", file)
        for file in os.listdir("tests")
        if file.lower().endswith(".xml")
    ]

    for xml_file in xml_files:
        name, _ = os.path.splitext(xml_file)
        py_file = "%s.py" % name
        yield (xml_file, py_file)


def main():
    for xml_file, py_file in get_files():
        print("Simulating %s ... " % colored(xml_file, attrs=["bold"]))
        sim_result = psim(read_file(xml_file), {}, {"quiet": True})
        test_result = run_tests(sim_result, py_file)
        if not test_result:
            sys.exit(1)


if __name__ == '__main__':
    main()
