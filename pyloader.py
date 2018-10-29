import os
import sys


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
