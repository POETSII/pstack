import json

from parser import read_poets_xml


def read_file(file):
    with open(file, 'r') as fid:
        return fid.read()


def main():
    file = 'output.xml'
    poets_xml = read_poets_xml(file)
    print json.dumps(poets_xml, indent=4)


if __name__ == '__main__':
    main()
