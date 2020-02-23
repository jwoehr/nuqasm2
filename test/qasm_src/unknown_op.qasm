// GHZ_XYY
OPENQASM 2.0 ;
include "qelib1.inc" ;
qreg q[3] ;
creg c[3] ;
x q[0] ;
h q[1] ;
h q[2] ;
cx q[1], q[0] ;
cx q[2], q[0] ;
h q[0] ;
h q[1] ;
h q[2] ;
// Here's an unknown op 'u(a,b,c)'
u(pi/2,pi/4,pi/15) q[0] ;
// Pauli gate: bit and phase flip
gate y a { u3(pi, pi/2, pi/2) a ; }
gate ch a,b {
h b ; sdg b ;
cx a, b ;
h b ; t b ;
cx a, b ;
t b ; h b ; s b ; x b ;
}

barrier q[0], q[1], q[2] ;
sdg q[0] ;
sdg q[1] ;
h q[0] ;
h q[1] ;
h q[2] ;
measure q[0] -> c[0] ;
measure q[1] -> c[1] ;
measure q[2] -> c[2] ;
