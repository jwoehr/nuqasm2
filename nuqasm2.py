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
from qasmast import (QasmTranslator, Qasm_Error)
import argparse
import sys
import datetime
import time
import pprint
import cProfile
import timeit
import gc

description = """Implements qasm2 translation to python data structures.
Working from _Open Quantum Assembly Language_
https://arxiv.org/pdf/1707.03429.pdf ......
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
Apache-2.0 license -- See LICENSE which you should have received with this code.
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

now = datetime.datetime.now().isoformat()

parser = argparse.ArgumentParser(description=description)

parser.add_argument("-o", "--outfile", action="store",
                    help="Write AST to outfile overwriting silently, default is stdout")
parser.add_argument("-p", "--profile", action="store_true",
                    help="Profile translator run")
parser.add_argument("-t", "--timeit", action="store_true",
                    help="Time translator run (1 iteration) (gc enabled)")
parser.add_argument("-u", "--unknown", action="store_true",
                    help="exit with error on unknown element in source")
parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
parser.add_argument("--save_pgm_source", action="store_true",
                    help="Save program source in output")
parser.add_argument("--save_element_source", action="store_true",
                    help="Save element source in output")
parser.add_argument("--save_gate_source", action="store_true",
                    help="Save gate source in output")
parser.add_argument("filepaths", nargs='*',
                    help="Filepath to 1 or more .qasm file(s) (default stdin)")

args = parser.parse_args()


epp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)


def verbosity(text, count):
    """Verbose error messages by level"""
    if args.verbose >= count:
        epp.pprint(text)


verbosity(args, 2)


def handle_error(ex, filepath):
    """Print out exception packet"""
    print("Error: " + filepath)
    x = ex.errpacket()
    epp.pprint(x)
    exit(x['errcode'])


if args.outfile:
    fout = open(args.outfile, 'w')
else:
    fout = sys.stdout

pp = pprint.PrettyPrinter(indent=4, stream=fout)

if args.filepaths:
    for filepath in args.filepaths:
        verbosity("Translating " + filepath, 1)
        qt = QasmTranslator.fromFile(filepath,
                                     no_unknown=args.unknown,
                                     datetime=datetime.datetime.now().isoformat(),
                                     save_pgm_source=args.save_pgm_source,
                                     save_element_source=args.save_element_source,
                                     save_gate_source=args.save_gate_source)
        try:
            if args.profile:
                cProfile.run('qt.translate()')
            elif args.timeit:
                print(">>>translation time", end=':')
                print(timeit.timeit(stmt='qt.translate()',
                                    setup='gc.enable()', number=1, globals=globals()))
            else:
                qt.translate()
        except Qasm_Error as ex:
            handle_error(ex, filepath)

        pp.pprint(qt.get_translation())

else:

    qt = QasmTranslator.fromFileHandle(sys.stdin, filepath=str(sys.stdin),
                                       no_unknown=args.unknown,
                                       datetime=datetime.datetime.now().isoformat(),
                                       save_pgm_source=args.save_pgm_source,
                                       save_element_source=args.save_element_source,
                                       save_gate_source=args.save_gate_source)
    try:
        if args.profile:
            cProfile.run('qt.translate()')
        elif args.timeit:
            print(">>>translation time", end=':')
            print(timeit.timeit(stmt='qt.translate()',
                                setup='gc.enable()', number=1, globals=globals()))
        else:
            qt.translate()
    except Qasm_Error as ex:
        handle_error(ex, str(sys.stdin))

    pp.pprint(qt.get_translation())


if fout is not sys.stdout:
    fout.close()

exit()

# end
