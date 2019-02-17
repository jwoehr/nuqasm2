"""
nuqasm2.py
Implement qasm2 translation to python data structures.
Working from _Open Quantum Assembly Language_
https://arxiv.org/pdf/1707.03429.pdf
jack j. woehr jwoehr@softwoehr.com po box 51 golden co 80402-0051
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
Apache-2.0 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
from qasmast import (QasmTranslator, Qasm_Declaration_Absent_Exception,
                     Qasm_Unknown_Element, Qasm_Gate_Missing_Open_Curly,
                     Qasm_Incomplete_Gate)
import argparse
import sys
import datetime
import time
import pprint

description = """Implement qasm2 translation to python data structures
Working from _Open Quantum Assembly Language_
https://arxiv.org/pdf/1707.03429.pdf
jack j. woehr jwoehr@softwoehr.com po box 51 golden co 80402-0051
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

now = datetime.datetime.now().isoformat()

parser = argparse.ArgumentParser(description=description)

parser.add_argument("-o", "--outfile", action="store",
                    help="Write AST to outfile overwriting silently, default is stdout")
parser.add_argument("-u", "--unknown", action="store_true",
                    help="exit with error on unknown element in source")
parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
parser.add_argument("filepaths", nargs='+',
                    help="Filepath(s) to one more .qasm file(s), required")

args = parser.parse_args()

# Verbose script


def verbosity(text, count):
    if args.verbose >= count:
        print(text)


def handle_error(ex, filepath):
    print("Error: " + filepath)
    x = ex.errpacket()
    pp.pprint(x)
    exit(x['errcode'])


if args.outfile:
    fout = open(args.outfile, 'w')
else:
    fout = sys.stdout

pp = pprint.PrettyPrinter(indent=4, stream=fout)

for filepath in args.filepaths:
    f = open(filepath, 'r')
    qasmsourcelines = []
    for line in f:
        qasmsourcelines.append(line.strip())
    qt = QasmTranslator(qasmsourcelines, filepath=filepath,
                        no_unknown=args.unknown,
                        datetime=datetime.datetime.now().isoformat())
    try:
        qt.translate()
    except Qasm_Declaration_Absent_Exception as ex:
        handle_error(ex, filepath)
    except Qasm_Unknown_Element as ex:
        handle_error(ex, filepath)
    except Qasm_Incomplete_Gate as ex:
        handle_error(ex, filepath)
    except Qasm_Gate_Missing_Open_Curly as ex:
        handle_error(ex, filepath)

    pp.pprint(qt.get_translation())

if fout is not sys.stdout:
    fout.close()

exit()

# end
