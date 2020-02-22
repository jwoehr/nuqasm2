OPENQASM 2.0;
include "qelib1.inc";
gate cxmol a,b {
        h b;
        cz a, b;
        h b;
}
gate swapmol a, b {
        cxmol a, b;
        cxmol b, a;
        cxmol a, b;
}
gate cczmol a, b, c {
        cu1(pi/2) b, c;
        cxmol a, b;
        cu1(pi/2) b, c;
        cxmol a, b;
        swapmol a, b;
        cu1(pi/2) b, c;
        swapmol a, b;
}
qreg q[3];
creg c[3];
x q[2];
x q[1];
h q[0];
cczmol q[2], q[1], q[0];
h q[0];
measure q->c;
