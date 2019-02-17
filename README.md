# nuqasm2
New qasm2 translator : qasm2 to Python dict form AST

Based on [Open Quantum Assembly Language](https://arxiv.org/pdf/1707.03429.pdf)

Translates QASM2 source into a Python dictionary.
* Filepath, datetime, and full source recorded for entire qasm program.
* The `ast` key is the entire program and is a list of element dictionaries, one per element of the program.
  * Within each line dict there are keys and values for
    * Line number
    * Original source
    * Element type
    * Parameter values
    * Any other appropriate translation elements

* This is a proof of concept.
  * The AST is intended to illustrate more than to prescribe.
  * Issues welcome, including comments and suggestions.

```
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

$ python nuqasm2.py yiqing.qasm
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
                   'reg_list': ['q[0]'],
                   'source': 'h q[0];',
                   'type': <ASTType.OP: 70>},
               {   'linenum': 7,
                   'op': 'h',
                   'reg_list': ['q[1]'],
                   'source': 'h q[1];',
                   'type': <ASTType.OP: 70>},
               {   'linenum': 8,
                   'op': 'h',
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
    'datetime': '2019-02-16T21:55:18.901432',
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
                  'measure q[2] -> c[2];',
                  '']}
```
