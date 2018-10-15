import sys
import pickle

from code import InteractiveConsole

from files import read_file
from files import write_file

class PythonInterpreter(InteractiveConsole):
    """Subclassed console that captures stdout

    adapted from https://stackoverflow.com/a/15311213
    """

    def __init__(self, available_functions=[], context_file=None):
        InteractiveConsole.__init__(self)
        self.context_file = context_file
        self.read_context()
        for func in available_functions:
            self.set(func.func_name, func)

    def showtraceback(self):
        self.exception_happened = True
        InteractiveConsole.showtraceback(self)

    def showsyntaxerror(self, filename=None):
        self.exception_happened = True
        InteractiveConsole.showsyntaxerror(self, filename)

    def push(self, expression):
        """Evaluate an expression"""
        self.exception_happened = False
        InteractiveConsole.push(self, expression)
        self.write_context()
        return ""

    def eval(self, cmd):
        """Alias for push"""
        return self.push(cmd)

    def call(self, method, kwargs={}):
        """Execute method and return results"""
        result = self.locals[method](**kwargs)
        self.write_context()
        return result

    def get(self, variable):
        return self.locals[variable]

    def set(self, variable, value):
        self.locals[variable] = value
        self.write_context()

    def write_context(self):
        if self.context_file:
            atoms ={key: val for key, val in self.locals.iteritems()
                    if type(val) in {int, float, str, bool}}
            write_file(self.context_file, pickle.dumps(atoms))

    def read_context(self):
        try:
            atoms = pickle.loads(read_file(self.context_file))
            for name, value in atoms.iteritems():
                self.set(name, value)
        except IOError:
            pass
