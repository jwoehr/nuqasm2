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

if args.filepaths:
    for filepath in args.filepaths:
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
        except Qasm_Declaration_Absent_Exception as ex:
            handle_error(ex, filepath)
        except Qasm_Unknown_Element as ex:
            handle_error(ex, filepath)
        except Qasm_Incomplete_Gate as ex:
            handle_error(ex, filepath)
        except Qasm_Gate_Missing_Open_Curly as ex:
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
