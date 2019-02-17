# nuqasm2
New qasm2 translator : qasm2 to Python dict form AST

Based on [Open Quantum Assembly Language](https://arxiv.org/pdf/1707.03429.pdf)

```
(venv_ibmqe) $ cat yiqing.qasm 
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

(venv_ibmqe) $ python nuqasm2.py yiqing.qasm 
{'filepath': 'yiqing.qasm', 'datetime': '2019-02-16T19:53:16.459932', 'source': ['// yiqing (one of many possible)', 'OPENQASM 2.0;', 'include "qelib1.inc";', 'qreg q[3];', 'creg c[3];', 'h q[0];', 'h q[1];', 'h q[2];', 'barrier q[0],q[1],q[2];', 'measure q[0] -> c[0];', 'measure q[1] -> c[1];', 'measure q[2] -> c[2];', ''], 'ast': [{'linenum': 1, 'type': <ASTType.COMMENT: 100>, 'source': '// yiqing (one of many possible)'}, {'linenum': 2, 'type': <ASTType.DECLARATION_QASM_2_0: 2000>, 'source': 'OPENQASM 2.0;'}, {'linenum': 3, 'type': <ASTType.INCLUDE: 3000>, 'source': 'include "qelib1.inc";', 'include': 'qelib1.inc'}, {'linenum': 4, 'type': <ASTType.QREG: 20>, 'source': 'qreg q[3];', 'qreg_name': 'q', 'qreg_num': '3'}, {'linenum': 5, 'type': <ASTType.CREG: 30>, 'source': 'creg c[3];', 'creg_name': 'c', 'creg_num': '3'}, {'linenum': 6, 'type': <ASTType.UNKNOWN: 0>, 'source': 'h q[0];'}, {'linenum': 7, 'type': <ASTType.UNKNOWN: 0>, 'source': 'h q[1];'}, {'linenum': 8, 'type': <ASTType.UNKNOWN: 0>, 'source': 'h q[2];'}, {'linenum': 9, 'type': <ASTType.BARRIER: 50>, 'source': 'barrier q[0],q[1],q[2];', 'reg_list': ['q[0]', 'q[1]', 'q[2]']}, {'linenum': 10, 'type': <ASTType.MEASURE: 40>, 'source': 'measure q[0] -> c[0];', 'source_reg': 'q[0]', 'target_reg': 'c[0]'}, {'linenum': 11, 'type': <ASTType.MEASURE: 40>, 'source': 'measure q[1] -> c[1];', 'source_reg': 'q[1]', 'target_reg': 'c[1]'}, {'linenum': 12, 'type': <ASTType.MEASURE: 40>, 'source': 'measure q[2] -> c[2];', 'source_reg': 'q[2]', 'target_reg': 'c[2]'}]}
```
