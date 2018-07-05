import json

from parser import read_poets_xml
from generator import generate_code


def read_file(file):
    with open(file, 'r') as fid:
        return fid.read()


def write_file(file, content):
    with open(file, 'w') as fid:
        fid.write(content)

def main():
    xml_file = 'tmp/output.xml'
    template_file = 'main.cpp'

    markup = read_poets_xml(xml_file)
    write_file('tmp/parsed.json', json.dumps(markup, indent=4))
    print generate_code(template_file, markup)


if __name__ == '__main__':
    main()
