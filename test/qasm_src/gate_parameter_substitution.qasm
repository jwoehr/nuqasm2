OPENQASM 2.0;

include "cu1mol.inc";

qreg q[3];
creg c[3];
x q[2];
x q[1];
h q[0];
cu1mol(pi) q[2], q[1], q[0];
h q[0];
measure q->c;