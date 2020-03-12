#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 17:16:04 2020
Turns nuqasm2 ast into Qiskit QuantumCircuit
@author: jax
"""

import ast
# import argparse
import os
import pprint
import re
import sys
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np  # pylint: disable-msg=unused-import
from .qasmast import ASTType, QasmTranslator


class ASTRegEx():  # pylint: disable-msg=too-few-public-methods
    """Regexes to use in processing AST"""
    OP = re.compile(r"(\w*)")
    ARGLIST = re.compile(r"\w*(.*)")


class ASTBinder(dict):
    """Bind reg list and param list w/r/t gate definition
    """

    def __init__(self, gate_definition, reg_list=None, param_list=None):
        """
        This binds the params.

        It may have a BUG!

        Do identical expansions match (and overwrite) different symbolic names?

        Parameters
        ----------
        gate_definition : dict
            nuqasm2 ast gate def.
        reg_list : list, optional
            list of c_sect code entry's registers, optional. The default is None.
        param_list : list, optional
            list of c_sect code entry's params, optional. The default is None.

        Returns
        -------
        None.

        """
        super(ASTBinder, self).__init__()
        self.param_bind = {}
        self.reg_bind = {}
        gate_param_list = gate_definition.get('gate_param_list')
        if gate_param_list:
            for i in range(0, len(gate_param_list)):  # pylint: disable-msg=consider-using-enumerate
                # self.param_bind.update({gate_param_list[i]: param_list[i]})
                self.param_bind.update({param_list[i]: gate_param_list[i]}) # bind backwards!
        gate_reg_list = gate_definition.get('gate_reg_list')
        if gate_reg_list:
            for i in range(0, len(gate_reg_list)):  # pylint: disable-msg=consider-using-enumerate
                self.reg_bind.update({gate_reg_list[i]: reg_list[i]})

    def param_binding(self, gate_param_name):
        """
        Return real param value for symbolic param name from gate definition.


        Parameters
        ----------
        gate_param_name : string
            symbolic param name from g_sect gate def.

        Returns
        -------
        Actual param value passed by caller of gate definition .

        """
        return self.param_bind.get(gate_param_name)

    def reg_binding(self, gate_reg_name):
        """
        Return real reg name for symbolic reg name from gate definition.

        Parameters
        ----------
        gate_reg_name : string
            symbolic reg name from g_sect gate def.

        Returns
        -------
        Actual reg passed by caller of gate defintion.

        """
        return self.reg_bind.get(gate_reg_name)

    def bind_regs(self, reg_list):
        """
        Return list of real reg names for list symbolic reg names from gate definition.

        Parameters
        ----------
        reg_list : list
            list of symbolic reg names used in gate definition.

        Returns
        -------
        b_list : list
            list of actual reg values from caller of gate definition.

        """
        b_list = None
        if reg_list:
            b_list = []
            for reg in reg_list:
                b_list.append(self.reg_binding(reg))
        return b_list

    def bind_params(self, param_list):
        """
        Return list of symbolic param names from gate definition
        that correspond to the runtime params that are provided.

        Parameters
        ----------
        param_list : list
            list of symbolic param names used in gate definition.

        Returns
        -------
        b_list : list
            list of actual param values from caller of gate definition.


        """
        b_list = None
        if param_list:
            b_list = []
            for param in param_list:
                bound_param = self.param_binding(param)
                # DEBUG
                # print("******bound_param {} param {} b_list {}".format(bound_param, param, b_list))  # pylint: disable-msg=line-too-long
                # END-DEBUG
                b_list.append(bound_param if bound_param else param)
        return b_list


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
        nuq2_ast : list, optional
            DESCRIPTION. nuqasm2 AST list to be turned into quantum circuite
        circuit : qiskit.circuit.QuantumCircuit, optional
            DESCRIPTION. Will be used if present. Otherwise, translate() creates
            new qiskit.circuit.QuantumCircuit
        stream : stream, optional
            DESCRIPTION. For message output, if any.
        loading_from_file : bool, optional
            DESCRIPTION. Are we loading a text representation of the AST?
            The default is False.

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

    @staticmethod
    def _match_entry_type_tuple(code_entry, type_tuple):
        """
        Does type of an AST entry match the type any AST type in type_tuple
        """
        entry_type = code_entry['type']
        return entry_type in type_tuple

    @staticmethod
    def _match_entry_type_string(code_entry, string_list):
        """
        Does string name of type of an AST entry match the
        string name of any AST type in string_list
        """
        entry_type = re.match(r"<(AST.*):.*", code_entry.get('type')).group(1)
        return bool(entry_type in string_list)

    def _match_entry_type(self, code_entry, type_tuple):
        """
        Is an AST entry of AST type we are looking for?
        """
        matched = False
        if self.loading_from_file:
            type_list = []
            for elem in type_tuple:
                type_list.append(str(elem))
            matched = self._match_entry_type_string(code_entry, type_list)
        else:
            matched = self._match_entry_type_tuple(code_entry, type_tuple)
        return matched

    def _marshall_regdefs(self):
        """Marshall the list of register declarations"""
        for entry in self.nuq2_ast['c_sect']:
            is_regdef = self._match_entry_type(entry,
                                               (ASTType.QREG,
                                                ASTType.CREG))
            if is_regdef:
                self.regdefs.append(entry)

    @staticmethod
    def _op_sig(op, arity):  # pylint: disable-msg=invalid-name
        """Compose operator signature to use as key with gatedefs"""
        return op + '/' + str(arity)

    def _marshall_gatedefs(self):
        """Make dictionary of gate definitions from AST"""
        for gatedef in self.nuq2_ast['g_sect']:
            gate_name = gatedef['gate_name']
            op = ASTRegEx.OP.match(gate_name).group(1)   # pylint: disable-msg=invalid-name
            arglist_match = ASTRegEx.ARGLIST.match(gate_name)
            arglist = arglist_match.group(1)
            arity = 0 if len(arglist) == 0 else len(arglist.split(','))
            self.gatedefs[self._op_sig(op, arity)] = gatedef

    def _create_quantum_circuit(self):
        """
        Instance a QuantumCircuit with the QRegs/CRegs called out in qasm code
        QReg and CReg entries already marshalled.
        """
        reg_list = []
        for entry in self.regdefs:
            is_qreg = self._match_entry_type(entry, [ASTType.QREG])

            if is_qreg:
                reg_list.append(QuantumRegister(entry.get('qreg_num'), entry.get('qreg_name')))
            else:
                reg_list.append(ClassicalRegister(entry.get('creg_num'), entry.get('creg_name')))

        self.circuit = QuantumCircuit(*reg_list)
        return self.circuit

    @staticmethod
    def _string_reg_to_reg(reg_name, qregs, cregs):
        """
        Nuqasm2 AST keeps register/bit operands as string.
        We must convert to actual reg.

        Parameters
        ----------
        reg_name : string
            Name of sought register
        qregs : list of QuantumRegister
            Seek reg here
        cregs : list of ClassicalRegister
            Seek reg here
        Returns
        -------
        Actual reg

        """

        reg = None
        if qregs:
            for r in qregs:  # pylint: disable-msg=invalid-name
                if r.name == reg_name:
                    reg = r
                    break
        if not reg:
            if cregs:
                for r in cregs:  # pylint: disable-msg=invalid-name
                    if r.name == reg_name:
                        reg = r
                        break
        return reg

    @staticmethod
    def _string_reg_to_bit(string_reg, qubits, clbits):
        """
        Nuqasm2 AST keeps register/bit operands as string.
        We must convert to actual bit.

        Parameters
        ----------
        circuit : QuantumCircuit(regs)
            Circuit to which the name reg belongs
        string_reg : string
            String representation of the reg/bit.
        qubits: list
            Individual qubits pertaining to circuit
        clbits: list
            Individual clbits pertaining to circuit
        Returns
        -------
        Actual bit

        """
        the_split = string_reg.split('[')
        reg_name = the_split[0]
        num = int(the_split[1].strip('[]'))
        bit = None

        if qubits:
            for b in qubits:  # pylint: disable-msg=invalid-name
                if b.register.name == reg_name:
                    if b.index == num:
                        bit = b
                        break
        if not bit:
            if clbits:
                for b in clbits:  # pylint: disable-msg=invalid-name
                    if b.register.name == reg_name:
                        if b.index == num:
                            bit = b
                            break

        return bit

    @staticmethod
    def _do_the_math(a_list):
        """
        substitute known string names of transcendentals with numpy equivs
        and do the math.

        Parameters
        ----------
        a_list : list of strings
            list of strings which may contain string names of transcendentals.

        Returns
        -------
        a_list : list
            the input list modified

        """
        b_list = []
        for i in a_list:
            i = i.replace('pi', "np.pi")
            # ...
            i = str(eval(i))  # pylint: disable-msg=eval-used
            b_list.append(i)
        return b_list

    def _op_append(self, entry, qregs, cregs, qubits, clbits):  # pylint: disable-msg=too-many-arguments, line-too-long
        """
        Append operation to circuit
        """

        string_reg_list = entry.get('reg_list')
        reg_list = []
        for string_reg in string_reg_list:
            if string_reg.find('[') >= 0:
                reg_list.append(self._string_reg_to_bit(string_reg, qubits, clbits))
            else:
                reg_list.append(self._string_reg_to_reg(string_reg, qregs, cregs))

        param_list = entry.get('param_list')
        if param_list:
            param_list = self._do_the_math(param_list)

        if not self._op_easy(entry.get('op'),
                             reg_list,
                             param_list=param_list if param_list else None):
            self._op_search(entry.get('op'),
                            reg_list,
                            param_list=param_list if param_list else None)

    def _op_easy(self, op, reg_list, param_list=None):  # pylint: disable-msg=invalid-name
        """
        Append operation to circuit where op is known to QuantumCircuit class

        Returns
        -------
        True IFF QuantumCircuit has this op

        """

        has_op = hasattr(self.circuit, op)

        if has_op:
            if param_list:
                # DEBUG
                # print("********** op {} param_list {} reg_list {}".format(op, param_list, reg_list))  # pylint: disable-msg=line-too-long
                # END-DEBUG
                getattr(self.circuit, op)(*param_list, *reg_list)
            else:
                getattr(self.circuit, op)(*reg_list)

        return has_op

    def _barrier_append(self, entry, qregs, qubits):
        """
        Append barrier to circuit
        """

        string_reg_list = entry.get('reg_list')
        reg_list = []
        for string_reg in string_reg_list:
            if string_reg.find('[') >= 0:
                reg_list.append(self._string_reg_to_bit(string_reg, qubits, None))
            else:
                reg_list.append(self._string_reg_to_reg(string_reg, qregs, None))

        getattr(self.circuit, 'barrier')(*reg_list)

    def _measure_append(self, entry, qregs, cregs, qubits, clbits):  # pylint: disable-msg=too-many-arguments, line-too-long
        """
        Append measure to circuit
        """
        source_reg = entry.get('source_reg')
        target_reg = entry.get('target_reg')
        reg_list = []

        if source_reg.find('[') >= 0:
            reg_list.append(self._string_reg_to_bit(source_reg, qubits, None))
        else:
            reg_list.append(self._string_reg_to_reg(source_reg, qregs, None))

        if target_reg.find('[') >= 0:
            reg_list.append(self._string_reg_to_bit(target_reg, None, clbits))
        else:
            reg_list.append(self._string_reg_to_reg(target_reg, None, cregs))

        getattr(self.circuit, 'measure')(*reg_list)

    def _unrollable(self, op_sig):
        """Does a op signature exist in the gate section?"""
        return self.gatedefs.get(op_sig)

    def _unroll(self, gate_definition, reg_list, param_list=None):  # pylint: disable-msg=invalid-name, line-too-long
        """Expand a gate definition"""
        ast_binder = ASTBinder(gate_definition, reg_list, param_list)
        for gate_op in gate_definition.get('gate_ops_list'):
            the_op = gate_op.get('op')
            the_reg_list = ast_binder.bind_regs(gate_op.get('op_reg_list'))
            the_param_list = None
            gate_op_param_list = gate_op.get('op_param_list')
            if gate_op_param_list:  # Have to subst in the full param for symbolic name.
                the_param_list = []
                param_symbolic_names = ast_binder.bind_params(param_list)
                # DEBUG
                # print('gate_op_param_list: {}'.format(str(gate_op_param_list)))
                # print(param_symbolic_names)
                # EMD=DEBUG
                for i in range(0, len(gate_op_param_list)):
                    if param_symbolic_names:
                        the_param_list.append(gate_op_param_list[i].replace(param_symbolic_names[i],
                                                                            param_list[i]))
                    else:
                        if gate_op_param_list:
                            the_param_list.append(gate_op_param_list[i])
            # DEBUG
            # print("******the_op {} the_reg_list {} the_param_list {}".format(the_op, the_reg_list, the_param_list))  # pylint: disable-msg=line-too-long
            # END-DEBUG
            if not self._op_easy(the_op,
                                 the_reg_list,
                                 param_list=the_param_list if the_param_list else None):
                self._op_search(the_op,
                                the_reg_list,
                                param_list=the_param_list if the_param_list else None)

    def _op_search(self, op, reg_list, param_list=None):  # pylint: disable-msg=invalid-name
        """
        Find an op in the gate definitions included
        """

        arity = 0
        if param_list:
            arity = len(param_list)

        gate_definition = self._unrollable(self._op_sig(op, arity))

        if gate_definition:
            self._unroll(gate_definition, reg_list, param_list)

    def translate(self):
        """
        Instance self.circuit from self.ast

        Returns
        -------
        TYPE, Ast2Circ
            DESCRIPTION. Ast2Circ self, to access attributes after translation.

        """
        self._marshall_gatedefs()
        self._marshall_regdefs()

        if not self.circuit:
            self._create_quantum_circuit()

        for entry in self.nuq2_ast['c_sect']:
            try:
                op_type = entry['type']
                if op_type is ASTType.OP:
                    starting_circuit_size = self.circuit.size()
                    self._op_append(entry, self.circuit.qregs, self.circuit.cregs,
                                    self.circuit.qubits, self.circuit.clbits)
                    if self.circuit.size() == starting_circuit_size:
                        raise Ast2CircOpNotFoundException(section='c_sect',
                                                          entry=entry)
                elif op_type is ASTType.BARRIER:
                    self._barrier_append(entry, self.circuit.qregs, self.circuit.qubits)
                elif op_type is ASTType.MEASURE:
                    self._measure_append(entry, self.circuit.qregs, self.circuit.cregs,
                                         self.circuit.qubits, self.circuit.clbits)
            except NameError as ex:
                raise Ast2CircTranslationException(section='c_sect',
                                                   entry=entry,
                                                   prev_ex=ex)

            else:  # It's nothing we care about in this stage
                pass
        return self

    @staticmethod
    def from_file(filepath):
        """
        Used in early testing to load stringified AST from file.
        May no longer work correctly at present.

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
        Ast2Circ
            instance with loaded stringified nuqasm2 AST.

        """
        if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
            raise Ast2CircException(filepath=filepath)
        file_handle = open(filepath, 'r')
        text = file_handle.read()
        file_handle.close()
        text = re.sub(r'(<ASTType\.\w*\: \d*>)', r"'\g<1>'", text)
        return Ast2Circ(nuq2_ast=ast.literal_eval(text), loading_from_file=True)

    @staticmethod
    def _from_qasm_str(text):
        text = re.sub(r'(<ASTType\.\w*\: \d*>)', r"'\g<1>'", text)
        return Ast2Circ(nuq2_ast=ast.literal_eval(text))

    @staticmethod
    def from_qasm_str(qasmsourcelines,  # pylint: disable-msg=too-many-arguments
                      name='main',
                      filepath=None,
                      no_unknown=False,
                      save_pgm_source=False, save_element_source=False,
                      save_gate_source=False,
                      show_gate_decls=False,
                      include_path='.'):
        """
        Loads qasm, translates, and returns a QuantumCircuit.
        Analogous to qiskit.circuit.QuantumCircuit.from_qasm_str()

        Parameters
        ----------
        qasmsourcelines : string or list of string
            Lines of OPENQASM2.0 to translate.
            Probably should be strip()'ed first.
        name: string, optional
            Name of circuit.
        filepath : string, optional
           Filepath from which string (opt arg to the AST stage).
           The default is None.
        no_unknown : bool, optional
            Exception in AST generation if unknown element.
            The default is False.
        save_pgm_source : bool, optional
            Save program source in AST. The default is False.
        save_element_source : bool, optional
            Save element source in AST. The default is False.
        save_gate_source : bool, optional
            Save gate source in AST. The default is False.
        show_gate_decls : bool, optional
            Show gate decls in of AST c_sect. The default is False.
        include_path : string, optional
            Path to search for included files. The default is '.'.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if type(qasmsourcelines) is str: # turn into list of string
            qasmsourcelines = qasmsourcelines.split(os.linesep)
        qt = QasmTranslator(qasmsourcelines,  # pylint: disable-msg=invalid-name
                            name=name,
                            filepath=filepath,
                            no_unknown=no_unknown,
                            save_pgm_source=save_pgm_source,
                            save_element_source=save_element_source,
                            save_gate_source=save_gate_source,
                            show_gate_decls=show_gate_decls,
                            include_path=include_path)
        qt.translate()
        ast2circ = Ast2Circ(nuq2_ast=qt.get_translation())
        return ast2circ.translate().circuit


class Ast2CircException(Exception):
    """Base class for Qasm exceptions"""

    def __init__(self,  # pylint: disable-msg=too-many-arguments
                 filepath=None,
                 section=None,
                 entry=None,
                 content=None,
                 prev_ex=None,
                 message=None):
        super(Ast2CircException, self).__init__()
        self.filepath = filepath
        self.section = section
        self.entry = entry
        self.content = content
        self.prev_ex = prev_ex
        self.message = message if message else str(type(self))
        self.errcode = 210

    def errpacket(self):
        "Get the error packet from exception as dict"
        ex = {'message': self.message,
              'section': self.section,
              'entry': self.entry,
              'content': self.content,
              'errcode': self.errcode,
              'prev_ex': self.prev_ex
              }
        return ex

class Ast2CircTranslationException(Ast2CircException):
    """Error on translation"""

    def __init__(self,  # pylint: disable-msg=too-many-arguments
                 filepath=None,
                 section=None,
                 entry=None,
                 content=None,
                 prev_ex=None,
                 message=None):
        super(Ast2CircTranslationException, self).__init__(filepath=filepath,
                                                           section=section,
                                                           entry=entry,
                                                           content=content,
                                                           prev_ex=prev_ex,
                                                           message=message)
        self.errcode = 220

class Ast2CircOpNotFoundException(Ast2CircException):
    """Error on translation"""

    def __init__(self,  # pylint: disable-msg=too-many-arguments
                 filepath=None,
                 section=None,
                 entry=None,
                 content=None,
                 prev_ex=None,
                 message=None):
        super(Ast2CircOpNotFoundException, self).__init__(filepath=filepath,
                                                          section=section,
                                                          entry=entry,
                                                          content=content,
                                                          prev_ex=prev_ex,
                                                          message=message)
        self.errcode = 221
# if __name__ == '__main__':

#     DESCRIPTION = """Implements qasm2 translation to python data structures.
#     Working from _Open Quantum Assembly Language_
#     https://arxiv.org/pdf/1707.03429.pdf ......
#     Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
#     Apache-2.0 license -- See LICENSE which you should have received with this code.
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#     """
#     PARSER = argparse.ArgumentParser(description=DESCRIPTION)

#     PARSER.add_argument("-f", "--filepath", action="store",
#                         help="nuqasm2 AST file to process")

#     ARGS = PARSER.parse_args()

#     if ARGS.filepath:
#         AST2CIRC = Ast2Circ.from_file(ARGS.filepath)
#         AST2CIRC.pp.pprint(AST2CIRC.nuq2_ast)
#         AST2CIRC._marshall_gatedefs()
#         AST2CIRC.pp.pprint(AST2CIRC.gatedefs)
#         AST2CIRC.translate()
#         AST2CIRC.pp.pprint(AST2CIRC.regdefs)
#         print(AST2CIRC.circuit)

#     sys.exit(0)
