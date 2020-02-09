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
from qasmast import(ASTType)

class ASTRegEx():  # pylint: disable-msg=too-few-public-methods
    """Regexes to use in processing AST"""
    OP = re.compile(r"(\w*)")
    ARGLIST = re.compile(r"\w*(.*)")

class Ast2Circ():
    """Turns nuqasm2 ast into Qiskit QuantumCircuit"""

    def __init__(self, ast=None, circuit=None, stream=sys.stdout):
        """Initialize instance"""
        self.reinit(ast, circuit, stream)

    def reinit(self, ast=None, circuit=None, stream=sys.stdout):
        "Reinitialize instance cold for re-use"
        self.circuit = circuit
        self.ast = ast
        self.spool = None
        self.gatedefs = {}
        self.pp = pprint.PrettyPrinter(indent=4, stream=stream)

    def marshall_gatedefs(self):
        """Make dictionary of gate definitions from AST"""
        for gatedef in self.ast['g_sect']:
            gate_name = gatedef['gate_name']
            op = ASTRegEx.OP.match(gate_name).group(1)
            arglist_match = ASTRegEx.ARGLIST.match(gate_name)
            arglist = arglist_match.group(1)
            arity = 0 if len(arglist) == 0 else len(arglist.split(','))
            self.gatedefs[op + '/' + str(arity)] = gatedef

    def unrollable(self, op_sig):
        """Does a op signature exist in the gate section?"""
        return self.gatedefs.hasattr(op_sig)

    def unroll(self, gate_invocation, gate_definition):
        """Expand a gate definition"""

    def translate(self):
        """Instance self.circuit from self.ast"""
        for code in self.ast['c_sect']:
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

    @staticmethod
    def from_file(filepath):
        """

        Parameters
        ----------
        filepath : string
            Filepath to nuqasm2 AST file.

        Raises
        ------
        Ast2CircException
            Raised if can't open file.

        Returns
        -------
        TYPE
            Ast2Circ instance with loaded AST.

        """
        if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
            raise Ast2CircException(filepath=filepath)
        file_handle = open(filepath, 'r')
        text = file_handle.read()
        file_handle.close()
        text = re.sub('(\<ASTType\.\w*\: \d*\>)', "'$1'", text)
        return Ast2Circ(ast=ast.literal_eval(text))

class Ast2CircException(Exception):
    """Base class for Qasm exceptions"""

    def __init__(self, filepath=None, linenum=None, line=None):
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
        ast2circ = Ast2Circ.from_file(ARGS.filepath)
        ast2circ.marshall_gatedefs()
        ast2circ.pp.pprint(ast2circ.gatedefs)

    sys.exit(0)
