OPENQASM 2.0;

// include "qelib1.inc";
gate cxmol a, b {
h b;
cz a, b;
h b;
}

// gate cu1mol(fred) a, b {
// u1(fred/2) a;
// cxmol a, b;
// u1(-fred/2) b;
// cxmol a, b;
// u1(fred/2) b;
// }

gate cu1mol(fred) a, b {
u1(fred/2) a;
cxmol a, b;
u1(-fred) b;
cxmol a, b;
u1(fred/2) b;
}
