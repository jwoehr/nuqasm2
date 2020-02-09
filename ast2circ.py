#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 17:16:04 2020
Turns nuqasm2 ast into Qiskit QuantumCircuit
@author: jax
"""

import ast
import argparse
import os
import pprint
import re
import sys
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qasmast import ASTType


class ASTRegEx():  # pylint: disable-msg=too-few-public-methods
    """Regexes to use in processing AST"""
    OP = re.compile(r"(\w*)")
    ARGLIST = re.compile(r"\w*(.*)")


class Ast2Circ():
    """Turns nuqasm2 ast into Qiskit QuantumCircuit"""

    def __init__(self,
                 nuq2_ast=None,
                 circuit=None,
                 stream=sys.stdout,
                 loading_from_file=False):
        """
        Initialize instance

        Parameters
        ----------
        nuq2_ast : TYPE, optional
            DESCRIPTION. The default is None.
        circuit : TYPE, optional
            DESCRIPTION. The default is None.
        stream : TYPE, optional
            DESCRIPTION. The default is sys.stdout.
        loading_from_file : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """

        self.circuit = circuit
        self.nuq2_ast = nuq2_ast
        self.loading_from_file = loading_from_file
        self.spool = None
        self.gatedefs = {}
        self.regdefs = []
        self.pp = pprint.PrettyPrinter(indent=4, stream=stream)   # pylint: disable-msg=invalid-name

    def reinit(self, nuq2_ast=None,
               circuit=None,
               stream=sys.stdout,
               loading_from_file=False):
        """

        Parameters
        ----------
        nuq2_ast : TYPE, optional
            DESCRIPTION. The default is None.
        circuit : TYPE, optional
            DESCRIPTION. The default is None.
        stream : TYPE, optional
            DESCRIPTION. The default is sys.stdout               loading_from_file=False.

        Returns
        -------
        None.

        """
        self.circuit = circuit
        self.nuq2_ast = nuq2_ast
        self.loading_from_file = loading_from_file
        self.spool = None
        self.gatedefs = {}
        self.regdefs = []
        self.pp = pprint.PrettyPrinter(indent=4, stream=stream)

    @staticmethod
    def match_entry_type_tuple(code_entry, type_tuple):
        """


        Parameters
        ----------
        code_entry : TYPE
            DESCRIPTION.
        type_tuple : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        entry_type = code_entry['type']
        return entry_type in type_tuple

    @staticmethod
    def match_entry_type_string(code_entry, string_list):
        """


        Parameters
        ----------
        code_entry : TYPE
            DESCRIPTION.
        string_list : TYPE
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        entry_type = re.match(r"<(AST.*):.*", code_entry.get('type')).group(1)
        # print('Debug: code entry type: ' +  entry_type)
        # print('Debug: string list: ' + str(string_list))
        return bool(entry_type in string_list)

    def match_entry_type(self, code_entry, type_tuple):
        """


        Parameters
        ----------
        code_entry : TYPE
            DESCRIPTION.
        type_tuple : TYPE
            DESCRIPTION.

        Returns
        -------
        matched : TYPE
            DESCRIPTION.

        """
        matched = False
        if self.loading_from_file:
            type_list = []
            for elem in type_tuple:
                type_list.append(str(elem))
            matched = self.match_entry_type_string(code_entry, type_list)
        else:
            matched = self.match_entry_type_tuple(code_entry, type_tuple)
        return matched

    def marshall_regdefs(self):
        """Marshall the list of register declarations"""
        for entry in self.nuq2_ast['c_sect']:
            is_regdef = self.match_entry_type(entry,
                                              (ASTType.QREG,
                                               ASTType.CREG)
                                              )
            if is_regdef:
                self.regdefs.append(entry)

    def marshall_gatedefs(self):
        """Make dictionary of gate definitions from AST"""
        for gatedef in self.nuq2_ast['g_sect']:
            gate_name = gatedef['gate_name']
            op = ASTRegEx.OP.match(gate_name).group(1)   # pylint: disable-msg=invalid-name
            arglist_match = ASTRegEx.ARGLIST.match(gate_name)
            arglist = arglist_match.group(1)
            arity = 0 if len(arglist) == 0 else len(arglist.split(','))
            self.gatedefs[op + '/' + str(arity)] = gatedef

    def unrollable(self, op_sig):
        """Does a op signature exist in the gate section?"""
        return self.gatedefs.get(op_sig)

    def unroll(self, gate_invocation, gate_definition):
        """Expand a gate definition"""

    def create_quantum_circuit(self):
        """


        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        reg_list = []
        for entry in self.regdefs:
            is_qreg = self.match_entry_type(entry, [ASTType.QREG])

            if is_qreg:
                reg_list.append(QuantumRegister(entry.get('qreg_num'), entry.get('qreg_name')))
            else:
                reg_list.append(ClassicalRegister(entry.get('creg_num'), entry.get('creg_name')))

        self.pp.pprint(reg_list)
        self.circuit = QuantumCircuit(*reg_list)
        return self.circuit

    def append_op(self, entry):
        """


        Parameters
        ----------
        entry : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """


    def translate(self):
        """
        Instance self.circuit from self.ast

        Returns
        -------
        TYPE, Ast2Circ
            DESCRIPTION. Ast2Circ self, to access attributes after translation.

        """
        self.marshall_gatedefs()
        self.marshall_regdefs()

        if not self.circuit:
            self.create_quantum_circuit()

        for code in self.nuq2_ast['c_sect']:
            op_type = code['type']
            if op_type is ASTType.QREG:
                pass
            elif op_type is ASTType.CREG:
                pass
            elif op_type is ASTType.OP:
                pass
            elif op_type is ASTType.BARRIER:
                pass
            elif op_type is ASTType.MEASURE:
                pass
            else:  # It's nothing we care about in this stage
                pass
        return self

    @staticmethod
    def from_file(filepath):
        """

        Parameters
        ----------
        filepath : string
            Filepath to nuqasm2 AST file.

        Raises
        ------
        TYPE. Ast2CircException
            DESCRIPTION. Raised if can't open file.

        Returns
        -------
        TYPE Ast2Circ
            DESCRIPTION. instance with loaded stringified nuqasm2 AST.

        """
        if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
            raise Ast2CircException(filepath=filepath)
        file_handle = open(filepath, 'r')
        text = file_handle.read()
        file_handle.close()
        text = re.sub(r'(<ASTType\.\w*\: \d*>)', r"'\g<1>'", text)
        return Ast2Circ(nuq2_ast=ast.literal_eval(text), loading_from_file=True)


class Ast2CircException(Exception):
    """Base class for Qasm exceptions"""

    def __init__(self, filepath=None, linenum=None, line=None):
        super(Ast2CircException, self).__init__()
        self.filepath = filepath
        self.linenum = linenum
        self.line = line
        self.message = "Ast2Circ_Exception"
        self.errcode = 10

    def errpacket(self):
        "Get the error packet from exception as dict"
        ex = {'message': self.message,
              'filename': self.filepath,
              'linenum': self.linenum,
              'line': self.line,
              'errcode': self.errcode
              }
        return ex


if __name__ == '__main__':

    DESCRIPTION = """Implements qasm2 translation to python data structures.
    Working from _Open Quantum Assembly Language_
    https://arxiv.org/pdf/1707.03429.pdf ......
    Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
    Apache-2.0 license -- See LICENSE which you should have received with this code.
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    """
    PARSER = argparse.ArgumentParser(description=DESCRIPTION)

    PARSER.add_argument("-f", "--filepath", action="store",
                        help="nuqasm2 AST file to process")

    ARGS = PARSER.parse_args()

    if ARGS.filepath:
        AST2CIRC = Ast2Circ.from_file(ARGS.filepath)
        AST2CIRC.pp.pprint(AST2CIRC.nuq2_ast)
        AST2CIRC.marshall_gatedefs()
        AST2CIRC.pp.pprint(AST2CIRC.gatedefs)
        AST2CIRC.translate()
        AST2CIRC.pp.pprint(AST2CIRC.regdefs)
        print(AST2CIRC.circuit)

    sys.exit(0)
