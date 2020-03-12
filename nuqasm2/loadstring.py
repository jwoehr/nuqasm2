#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 13:41:36 2020

@author: jax
"""
from nuqasm2 import Ast2Circ

def load_string(qasm_string, include_path=None):
    """

    Parameters
    ----------
    qasm_string : string
        OPENQASM 2.x source to be assembled to qiskit.QuantumCircuit
    include_path : string, optional
        Include path list, e.g., for finding qelib1.inc. The default is None.

    Returns
    -------
    circ : qiskit.QuantumCircuit
       qiskit.QuantumCircuit representing the qasm string passed in to func.

    """
    circ = Ast2Circ.from_qasm_str(qasm_string,
                                  include_path=include_path,
                                  no_unknown=True)
    return circ
