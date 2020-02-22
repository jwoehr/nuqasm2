OPENQASM 2.0;
include "qelib1.inc";
gate test a, b{
    h b;
    cz a, b;
    h b;
}
qreg q[2];
creg c[2];
x q[1];
test q[1], q[0];
measure q->c;

