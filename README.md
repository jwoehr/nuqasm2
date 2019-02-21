# nuqasm2
New qasm2 translator : qasm2 to Python dict form AST

Based on [Open Quantum Assembly Language](https://arxiv.org/pdf/1707.03429.pdf)

Translates QASM2 source into a Python dictionary.
* Filepath, datetime, and full source recorded for entire qasm program.
* The `user_gates` key is the list definitions (if any) of user-defined gates.
* The `ast` key is the program and is a list of element dictionaries, one per element of the program.
  * Within each dict in `ast` there are keys and values for
    * Line number
    * Original source
    * Element type
    * Parameter values
    * Any other appropriate translation elements

* This is a proof of concept.
  * The AST is intended to illustrate more than to prescribe.
  * Issues welcome, including comments and suggestions.

```
$ python nuqasm2.py -h
usage: nuqasm2.py [-h] [-o OUTFILE] [-p] [-t] [-u] [-v] [--save_pgm_source]
                  [--save_element_source] [--save_gate_source] [--save_source]
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
  -o OUTFILE, --outfile OUTFILE
                        Write AST to outfile overwriting silently, default is
                        stdout
  -p, --profile         Profile translator run
  -t, --timeit          Time translator run (1 iteration) (gc enabled)
  -u, --unknown         exit with error on unknown element in source
  -v, --verbose         Increase verbosity each -v up to 3
  --save_pgm_source     Save program source in output
  --save_element_source
                        Save element source in output
  --save_gate_source    Save gate source in output
  --save_source         Save all source regions of output (equivalent to
                        --save_pgm_source --save_element_source
                        --save_gate_source)
$ cat yiqing.qasm
// yiqing (one of many possible)
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
h q[1];
h q[2];
barrier q[0],q[1],q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
$ python nuqasm2.py --save_source yiqing.qasm
{   'ast': [   {   'linenum': 1,
                   'source': '// yiqing (one of many possible)',
                   'type': <ASTType.COMMENT: 100>},
               {   'linenum': 2,
                   'source': 'OPENQASM 2.0;',
                   'type': <ASTType.DECLARATION_QASM_2_0: 2000>},
               {   'include': 'qelib1.inc',
                   'linenum': 3,
                   'source': 'include "qelib1.inc";',
                   'type': <ASTType.INCLUDE: 3000>},
               {   'linenum': 4,
                   'qreg_name': 'q',
                   'qreg_num': '3',
                   'source': 'qreg q[3];',
                   'type': <ASTType.QREG: 20>},
               {   'creg_name': 'c',
                   'creg_num': '3',
                   'linenum': 5,
                   'source': 'creg c[3];',
                   'type': <ASTType.CREG: 30>},
               {   'linenum': 6,
                   'op': 'h',
                   'param_list': None,
                   'reg_list': ['q[0]'],
                   'source': 'h q[0];',
                   'type': <ASTType.OP: 70>},
               {   'linenum': 7,
                   'op': 'h',
                   'param_list': None,
                   'reg_list': ['q[1]'],
                   'source': 'h q[1];',
                   'type': <ASTType.OP: 70>},
               {   'linenum': 8,
                   'op': 'h',
                   'param_list': None,
                   'reg_list': ['q[2]'],
                   'source': 'h q[2];',
                   'type': <ASTType.OP: 70>},
               {   'linenum': 9,
                   'reg_list': ['q[0]', 'q[1]', 'q[2]'],
                   'source': 'barrier q[0],q[1],q[2];',
                   'type': <ASTType.BARRIER: 50>},
               {   'linenum': 10,
                   'source': 'measure q[0] -> c[0];',
                   'source_reg': 'q[0]',
                   'target_reg': 'c[0]',
                   'type': <ASTType.MEASURE: 40>},
               {   'linenum': 11,
                   'source': 'measure q[1] -> c[1];',
                   'source_reg': 'q[1]',
                   'target_reg': 'c[1]',
                   'type': <ASTType.MEASURE: 40>},
               {   'linenum': 12,
                   'source': 'measure q[2] -> c[2];',
                   'source_reg': 'q[2]',
                   'target_reg': 'c[2]',
                   'type': <ASTType.MEASURE: 40>}],
    'datetime': '2019-02-20T21:22:08.696377',
    'filepath': 'yiqing.qasm',
    'source': [   '// yiqing (one of many possible)',
                  'OPENQASM 2.0;',
                  'include "qelib1.inc";',
                  'qreg q[3];',
                  'creg c[3];',
                  'h q[0];',
                  'h q[1];',
                  'h q[2];',
                  'barrier q[0],q[1],q[2];',
                  'measure q[0] -> c[0];',
                  'measure q[1] -> c[1];',
                  'measure q[2] -> c[2];'],
    'user_gates': []}

```
