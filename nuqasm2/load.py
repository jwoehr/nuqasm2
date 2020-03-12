#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 13:41:36 2020

@author: jax
"""
from typing import List
from qiskit import QuantumCircuit
from nuqasm2 import Ast2Circ, Ast2CircException

def load_from_string(qasm_string: str or List[str], include_path: str = None) -> QuantumCircuit:
    """

    Parameters
    ----------
    qasm_string : string or List[str]
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

def load_from_file(path: str, include_path: str = None) -> QuantumCircuit:
    """

    Parameters
    ----------
    path : string
        path to OPENQASM 2.x source to be assembled to qiskit.QuantumCircuit
    include_path : string, optional
        Include path list, e.g., for finding qelib1.inc. The default is None.

    Returns
    -------
    circ : qiskit.QuantumCircuit
       qiskit.QuantumCircuit representing the qasm string passed in to func.

    """
    _file = open(path, 'r')
    qasm_string = _file.read()
    _file.close()
    circ = Ast2Circ.from_qasm_str(qasm_string,
                                  include_path=include_path,
                                  no_unknown=True)
    return circ

def load(filename: str = None,
         data: str = None,
         include_path: str = None) -> QuantumCircuit:
    """


    Parameters
    ----------
    filename : str, optional
        Filepath to qasm program source. The default is None.
    data : str or List[str], optional
        Qasm program source as string or list of string. The default is None.
    include_path : str, optional
        Include path for qasm include directives.. The default is None.

    Raises
    ------
    Ast2CircException
        If both or neither filename and data are present.

    Returns
    -------
    QuantumCircuit
        The factoried circuit.

    """

    if (not data and not filename) or (data and filename):
        raise Ast2CircException("To load, either filename or data (and not both) must be provided.")
    circ = None
    if data:
        circ = load_from_string(data, include_path=include_path)
    elif filename:
        circ = load_from_file(filename, include_path=include_path)
    return circ
