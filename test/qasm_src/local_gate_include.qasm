// foo.qasm ... test nuqasm2 unroll
OPENQASM 2.0;
include "qelib1.inc";
include "foogate.inc";
qreg q[3];
creg c[3];
rx(pi/2) q[0];
foo q[0], q[1], q[2];
measure q -> c;
