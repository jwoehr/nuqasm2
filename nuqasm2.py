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
if __name__ == '__main__':
    import os
    import io
    import gc
    import timeit
    import pstats
    import cProfile
    import pprint
    import time
    import datetime
    import sys
    import argparse
    from qasmast import (QasmTranslator, Qasm_Exception)

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

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-n", "--name", action="store", default='main',
                        help="Give a name to the translation unit (default 'main'")
    parser.add_argument("-o", "--outfile", action="store",
                        help="Write AST to outfile overwriting silently, default is stdout")
    parser.add_argument("-p", "--profile", action="store_true",
                        help="""Profile translator run, writing to stderr and also
                        to file if --perf_filepath switch is also used""")
    parser.add_argument("-i", "--include_path", action="store", default='.',
                        help="Search path for includes, paths separated by '" +
                        os.pathsep + "', default include path is '.'")
    parser.add_argument("--perf_filepath", action="store",
                        help="Save -p --profile data to provided filename")
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
    parser.add_argument("--save_source", action="store_true",
                        help="""Save all source regions of output (equivalent to
                        --save_pgm_source --save_element_source --save_gate_source)
                        """)
    parser.add_argument("--show_gate_decls", action="store_true",
                        help="Show gate declarations in code section output")
    parser.add_argument("--sortby", action="store", default="cumtime",
                        help="""Sort sequence for performance data if -p switch
                        used ... one or more of the following separated by spaces
                        in a single string on the command line, e.g., --sortby
                        "calls cumtime file" :
                        'calls' == call count
                        'cumtime' == cumulative time
                        'file' == file name
                        'module' == file name
                        'ncalls' == call count
                        'pcalls' == primitive call count
                        'line' == line number
                        'name' == function name
                        'nfl' == name/file/line
                        'stdname' == standard name
                        'time' == internal time
                        'tottime' == internal time
                        ... default is cumtime
                        """)

    parser.add_argument("filepaths", nargs='*',
                        help="Filepath to 1 or more .qasm file(s) (default stdin)")

    args = parser.parse_args()

    epp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)

    def verbosity(text, count):
        """Verbose error messages by level"""
        if args.verbose >= count:
            epp.pprint(text)

    verbosity(args, 3)

    def handle_error(ex, filepath):
        """Print out exception packet"""
        epp.pprint("Error: " + filepath)
        x = ex.errpacket()
        epp.pprint(x)
        exit(x['errcode'])

    if args.outfile:
        fout = open(args.outfile, 'w')
    else:
        fout = sys.stdout

    pp = pprint.PrettyPrinter(indent=4, stream=fout)

    def profileTranslate(qt, sortby=args.sortby):
        """
        Profile a translation run and write it to stderr
        and optionally to perf_filepath
        """
        pr = cProfile.Profile()
        pr.enable()
        qt.translate()
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        pss = ps.print_stats()
        sys.stderr.write(s.getvalue())
        if args.perf_filepath:
            verbosity("Performance filepath is " + args.perf_filepath, 2)
            f = open(args.perf_filepath, 'w')
            f.write(s.getvalue())
            f.close()

    if args.filepaths:
        for filepath in args.filepaths:
            verbosity("Translating " + filepath, 1)
            qt = QasmTranslator.fromFile(filepath, name=args.name,
                                         no_unknown=args.unknown,
                                         save_pgm_source=args.save_pgm_source or args.save_source,
                                         save_element_source=args.save_element_source or args.save_source,
                                         save_gate_source=args.save_gate_source or args.save_source,
                                         show_gate_decls=args.show_gate_decls,
                                         include_path=args.include_path)
            try:
                if args.profile:
                    profileTranslate(qt)

                elif args.timeit:
                    print(">>>translation time", end=':')
                    print(timeit.timeit(stmt='qt.translate()',
                                        setup='gc.enable()', number=1, globals=globals()))
                else:
                    qt.translate()
            except Qasm_Exception as ex:
                handle_error(ex, filepath)

            pp.pprint(qt.get_translation())

    else:

        qt = QasmTranslator.fromFileHandle(sys.stdin, name=args.name, filepath=str(sys.stdin),
                                           no_unknown=args.unknown,
                                           datetime=datetime.datetime.now().isoformat(),
                                           save_pgm_source=args.save_pgm_source or args.save_source,
                                           save_element_source=args.save_element_source or args.save_source,
                                           save_gate_source=args.save_gate_source or args.save_source,
                                           show_gate_decls=args.show_gate_decls,
                                           include_path=args.include_path)
        try:
            if args.profile:
                profileTranslate(qt)
            elif args.timeit:
                print(">>>translation time", end=':')
                print(timeit.timeit(stmt='qt.translate()',
                                    setup='gc.enable()', number=1, globals=globals()))
            else:
                qt.translate()
        except Qasm_Exception as ex:
            handle_error(ex, str(sys.stdin))

        pp.pprint(qt.get_translation())

    if fout is not sys.stdout:
        fout.close()

    exit()

# end
