# nuqasm2

New OPENQASM 2.0 translator to work with [Qiskit](https://github.com/Qiskit).

The current release is [v0.32](https://github.com/jwoehr/nuqasm2/releases/tag/v0.32). This README is on the `master` branch and may reflect changes that have occurred since the last release.

`nuqasm2` comes with NO WARRANTY and NO GUARANTEE of correctness nor of applicability of use. See LICENSE.

`nuqasm2` now generates [`qiskit.circuit.QuantumCircuit`](https://qiskit.org/documentation/_modules/qiskit/circuit/quantumcircuit.html)
from nuqasm2 AST.

Tne `nuqasm2` command itself is a test driver: the companion project [`qis_job`](https://github.com/jwoehr/qis_job)
optionally uses `nuqasm2` code to assemble OPENQASM 2.O instead of using the Qiskit qasm parser.

This work is based on [Open Quantum Assembly Language](https://arxiv.org/pdf/1707.03429.pdf)

Thanks to the authors of that work and to the IBM Qiskit Team, a world-class research and development group.

`nuqasm2/qasmast` is the class file that translates OPENQASM 2.O source into a Python dictionary with 4 keys:

* `t_sect`
  * Filepaths
  * Datetimes
  * Name of unit
* `c_sect`
  * Ops
  * Declarations
  * Comments
* `g_sect`
  * User gate definitions (e.g., `qelib1.inc`)
* `s_sect`
  * Saved source

There are many options controlling what gets generated.

There is a [detailed explanation of the Abstract Syntax Tree (AST) output](https://github.com/jwoehr/nuqasm2/blob/master/doc/nuqasm_ast.md) in the `doc/` directory


Output can include
* Source file path
* Line number
* Original source
* Element type
* Parameter values
* Other appropriate translation elements

`nuqasm2/ast2circ` is the class file that converts nuqasm2 AST to `qiskit.circuit.QuantumCircuit`

*Note* that when using the `nuqasm2` command, any qasm source file which does `include "qelib1.inc";` will need `qelib.inc`
either to be in the current directory, or in a directory mentioned to the ` -i --include_path` directive.

[Issues](https://github.com/jwoehr/nuqasm2/issues) welcome, including comments and suggestions.

```
$ nuqasm2 -h
usage: nuqasm2 [-h] [-n NAME] [-o OUTFILE] [-i INCLUDE_PATH] [-a] [-c] [-d]
               [-p | -t] [--perf_filepath PERF_FILEPATH] [-q] [-u] [-v]
               [--save_pgm_source] [--save_element_source]
               [--save_gate_source] [--save_source] [--show_gate_decls]
               [--sortby SORTBY]
               [filepaths [filepaths ...]]

Implements qasm2 translation to python data structures. Working from _Open
Quantum Assembly Language_ https://arxiv.org/pdf/1707.03429.pdf ......
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO
80402-0051. Apache-2.0 license -- See LICENSE which you should have received
with this code. Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See
the License for the specific language governing permissions and limitations
under the License.

positional arguments:
  filepaths             Filepath to 1 or more .qasm file(s) (default stdin)

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Give a name to the translation unit (default 'main'
  -o OUTFILE, --outfile OUTFILE
                        File to which to write output overwriting silently,
                        default is stdout
  -i INCLUDE_PATH, --include_path INCLUDE_PATH
                        Search path for includes, paths separated by ':',
                        default include path is '.'
  -a, --ast             print the AST
  -c, --circuit         Generate circuit
  -d, --draw            Draw generated circuit
  -p, --profile         Profile translator run, writing to stderr and also to
                        file if --perf_filepath switch is also used (-p,
                        --profile is mutually exclusive with -t, --timeit)
  -t, --timeit          Time translator run (1 iteration) (gc enabled) (-t,
                        --timeit is mutually exclusive with -p, --profile)
  --perf_filepath PERF_FILEPATH
                        Save -p --profile data to provided filename
  -q, --qasm            with -c, output qasm from completed circuit
  -u, --unknown         exit with error on unknown element in source
  -v, --verbose         Increase verbosity each -v up to 3
  --save_pgm_source     Save program source in output
  --save_element_source
                        Save element source in output
  --save_gate_source    Save gate source in output
  --save_source         Save all source regions of output (equivalent to
                        --save_pgm_source --save_element_source
                        --save_gate_source)
  --show_gate_decls     Show gate declarations in code section output
  --sortby SORTBY       Sort sequence for performance data if -p switch used
                        ... one or more of the following separated by spaces
                        in a single string on the command line, e.g., --sortby
                        "calls cumtime file" : 'calls' == call count 'cumtime'
                        == cumulative time 'file' == file name 'module' ==
                        file name 'ncalls' == call count 'pcalls' == primitive
                        call count 'line' == line number 'name' == function
                        name 'nfl' == name/file/line 'stdname' == standard
                        name 'time' == internal time 'tottime' == internal
                        time ... default is cumtime

$ cat foogate.inc
/ foogate.inc
// Testing nuqasm2 unroll
// C3 gate: Toffoli
gate foo a,b,c
{
  h c;
  cx b,c; tdg c;
  cx a,c; t c;
  cx b,c; tdg c;
  cx a,c; t b; t c; h c;
  cx a,b; t a; tdg b;
  cx a,b;
}

$ cat foo.qasm

// foo.qasm ... test nuqasm2 unroll
OPENQASM 2.0;
include "qelib1.inc";
include "foogate.inc";
qreg q[3];
creg c[3];
rx(pi/2) q[0];
foo q[0], q[1], q[2];
measure q -> c;

$ nuqasm2 -c -d -i ~/work/QISKit/DEV/qiskit-terra/qiskit/qasm/libs:. foo.qasm
        ┌────────────────────────┐                                             ┌───┐      ┌─┐   
q_0: |0>┤ Rx(1.5707963267948966) ├──────────────■─────────────────────■────■───┤ T ├───■──┤M├───
        └────────────────────────┘              │             ┌───┐   │  ┌─┴─┐┌┴───┴┐┌─┴─┐└╥┘┌─┐
q_1: |0>────────────────────────────■───────────┼─────────■───┤ T ├───┼──┤ X ├┤ Tdg ├┤ X ├─╫─┤M├
                  ┌───┐           ┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌┴───┴┐┌─┴─┐├───┤└┬───┬┘└┬─┬┘ ║ └╥┘
q_2: |0>──────────┤ H ├───────────┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ T ├─┤ H ├──┤M├──╫──╫─
                  └───┘           └───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘ └───┘  └╥┘  ║  ║ 
 c_0: 0 ═══════════════════════════════════════════════════════════════════════════════╬═══╩══╬═
                                                                                       ║      ║ 
 c_1: 0 ═══════════════════════════════════════════════════════════════════════════════╬══════╩═
                                                                                       ║        
 c_2: 0 ═══════════════════════════════════════════════════════════════════════════════╩════════

```
