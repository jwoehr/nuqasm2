"""
qasmast.py
Classes to implement qasm2 translation to python data structures
Working from _Open Quantum Assembly Language_
https://arxiv.org/pdf/1707.03429.pdf
jack j. woehr jwoehr@softwoehr.com po box 51 golden co 80402-0051
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
Apache-2.0 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
from enum import Enum
import re


class QTRegEx():
    COMMENT = re.compile(r"^\s*//")
    INCLUDE = re.compile(r"^\s*include\s+\"\S+\"\s*;")
    QREG = re.compile(r"^\s*qreg\s+\S*\[\d+\]\s*;")
    CREG = re.compile(r"^\s*creg\s+\S*\[\d+\]\s*;")
    MEASURE = re.compile(r"^\s*measure\s+\S+\s+\-\>\s+\S+\s*;")
    BARRIER = re.compile(r"^\s*barrier\s+.*;")
    GATE = re.compile(r"^\s*gate\s+.*")
    OP = re.compile(r"^\s*\S+\s+\S+\[\d+\]\s*;")

    INCLUDE_TARGET = re.compile(r".*\"(\S+)\"\s*;")
    REG_DECL = re.compile(r".*(\S+)\[(\d+)\].*")
    MEASURE_DECL = re.compile(r"^\s*measure\s+(\S+)\s+\-\>\s+(\S+)\s*;")
    BARRIER_DECL = re.compile(r"\S+\[\d+\]")
    OP_AND_ARGS = re.compile(r"^\s*(\S+)\s+.*")
    OP_PARAM_LIST = re.compile(r"(\S+)\((.*)\)")
    OP_REG_LIST = re.compile(r"\S+\[\d+\]")

    START_CURLY = re.compile(r".*\{.*")
    END_CURLY = re.compile(r".*\}.*")
    GATE_DECL = re.compile(r"gate\s+(\S+)\s+(\S*).*")
    GATE_OPS = re.compile(r"gate\s+.*\{(.*)\}")
    GATE_OPS_LIST = re.compile(r"\S+\s+\S+;")
    GATE_OP = re.compile(r"(\w+).*")
    GATE_OP_PARAMS = re.compile(r"\S+\((.*)\).*")
    GATE_OP_REGS = re.compile(r".*\s+(\S+);")


class ASTType(Enum):
    UNKNOWN = 0
    COMMENT = 100
    QREG = 20
    CREG = 30
    MEASURE = 40
    BARRIER = 50
    GATE = 60
    OP = 70
    BLANK = 1000
    DECLARATION_QASM_2_0 = 2000
    INCLUDE = 3000

    @classmethod
    def astType(cls, source):
        if source == '':
            return cls.BLANK
        if source == "OPENQASM 2.0;":
            return cls.DECLARATION_QASM_2_0
        x = QTRegEx.COMMENT.search(source)
        if x:
            return cls.COMMENT
        x = QTRegEx.INCLUDE.search(source)
        if x:
            return cls.INCLUDE
        x = QTRegEx.QREG.search(source)
        if x:
            return cls.QREG
        x = QTRegEx.CREG.search(source)
        if x:
            return cls.CREG
        x = QTRegEx.MEASURE.search(source)
        if x:
            return cls.MEASURE
        x = QTRegEx.BARRIER.search(source)
        if x:
            return cls.BARRIER
        x = QTRegEx.GATE.search(source)
        if x:
            return cls.GATE
        x = QTRegEx.OP.search(source)
        if x:
            return cls.OP
        return cls.UNKNOWN


class ASTElement():
    """
    ASTElement
    Superclass of all ASTElement classes
    Knows linenum, ast_type, source, text
    linenum is source array line number
    source is source code
    """

    def __init__(self, linenum, ast_type, source):
        self.linenum = linenum
        self.ast_type = ast_type
        self.source = source

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type, 'source': self.source}


class ASTElementUnknown(ASTElement):
    """
    ASTElementUnknown
    An unknown ASTElement, unimplemented or error
    Knows linenum, ast_type, source
    """

    def __init__(self, linenum, source):
        super(ASTElementUnknown, self).__init__(
            linenum, ASTType.UNKNOWN, source)


class ASTElementComment(ASTElement):
    """
    ASTElementComment
    A programmer comment element
    Knows linenum, ast_type, source
    """

    def __init__(self, linenum, source):
        super(ASTElementComment, self).__init__(
            linenum, ASTType.COMMENT, source)


class ASTElementDeclarationQasm2_0(ASTElement):
    """
    ASTElementDeclarationQasm2_0
    Obligatory declaration
    Knows linenum, ast_type, source
    """

    def __init__(self, linenum, source):
        super(ASTElementDeclarationQasm2_0, self).__init__(
            linenum, ASTType.DECLARATION_QASM_2_0, source)


class ASTElementInclude(ASTElement):
    """
    ASTElementInclude
    A programmer comment element
    Knows linenum, ast_type, source, include
    """

    def __init__(self, linenum, source):
        super(ASTElementInclude, self).__init__(
            linenum, ASTType.INCLUDE, source)
        x = QTRegEx.INCLUDE_TARGET.search(source)
        self.include = x.group(1)

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'include': self.include}


class ASTElementQReg(ASTElement):
    """
    ASTElementQReg
    A QReg declaration
    Knows linenum, ast_type, source, qreg_name, qreg_num
    """

    def __init__(self, linenum, source):
        super(ASTElementQReg, self).__init__(linenum, ASTType.QREG, source)
        x = QTRegEx.REG_DECL.match(self.source)
        self.qreg_name = x.group(1)
        self.qreg_num = x.group(2)

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'qreg_name': self.qreg_name, 'qreg_num': self.qreg_num}


class ASTElementCReg(ASTElement):
    """
    ASTElementCReg
    A CReg declaration
    Knows linenum, ast_type, source, creg_name, creg_num
    """

    def __init__(self, linenum, source):
        super(ASTElementCReg, self).__init__(linenum, ASTType.CREG, source)
        x = QTRegEx.REG_DECL.match(self.source)
        self.creg_name = x.group(1)
        self.creg_num = x.group(2)

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'creg_name': self.creg_name, 'creg_num': self.creg_num}


class ASTElementMeasure(ASTElement):
    """
    ASTElementMeasure
    A measurement
    Knows linenum, ast_type, source, source_reg, target_reg
    """

    def __init__(self, linenum, source):
        super(ASTElementMeasure, self).__init__(
            linenum, ASTType.MEASURE, source)
        x = QTRegEx.MEASURE_DECL.match(self.source)
        self.source_reg = x.group(1)
        self.target_reg = x.group(2)

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'source_reg': self.source_reg, 'target_reg': self.target_reg}


class ASTElementBarrier(ASTElement):
    """
    ASTElementBarrier
    A barrier
    Knows linenum, ast_type, source, reg_list
    """

    def __init__(self, linenum, source):
        super(ASTElementBarrier, self).__init__(
            linenum, ASTType.BARRIER, source)
        x = QTRegEx.BARRIER_DECL.findall(self.source)
        self.reg_list = x[0].split(',')

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'reg_list': self.reg_list}


class ASTElementOp(ASTElement):
    """
    ASTElementOp
    An operator
    Knows linenum, ast_type, source, op, param_list, reg_list
    """

    def __init__(self, linenum, source):
        super(ASTElementOp, self).__init__(linenum, ASTType.OP, source)
        x = QTRegEx.OP_AND_ARGS.match(self.source)
        op_and_args = x.group(1)
        x = QTRegEx.OP_PARAM_LIST.match(op_and_args)

        self.param_list = None
        if x:
            self.op = x.group(1)
            self.param_list = x.group(2).split(',')
        else:
            self.op = op_and_args

        x = QTRegEx.OP_REG_LIST.findall(self.source)
        self.reg_list = x[0].split(',')

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'op': self.op,
                'param_list': self.param_list, 'reg_list': self.reg_list}


class QasmTranslator():

    def __init__(self, qasmsourcelines, filepath=None, datetime=None,
                 no_unknown=False):
        self.qasmsourcelines = qasmsourcelines
        self.translation = {
            'filepath': filepath, 'datetime': datetime,
            'source': qasmsourcelines, 'user_gates': [],
            'ast': []}
        self.no_unknown = no_unknown

    def get_filepath(self):
        return self.translation['filepath']

    def get_datetime(self):
        return self.translation['datetime']

    def get_ast(self):
        return self.translation['ast']

    def get_nth_ast(self, n):
        return self.get_ast[n]

    def get_nth_ast_type(self, n):
        return self.get_nth_ast['type']

    def get_nth_ast_element(self, n):
        return self.get_nth_ast['element']

    def get_nth_ast_source(self, n):
        return self.get_nth_ast['source']

    def get_nth_ast_text(self, n):
        return self.get_nth_ast['text']

    def get_source():
        return self.translation['source']

    def append_ast(self, ast):
        self.translation['ast'].append(ast)

    def get_user_gates(self):
        return self.translation['user_gates']

    def get_nth_user_gate(self, index):
        return self.get_user_gates()[index]

    def append_user_gate(self, user_gate):
        self.translation['user_gates'].append(user_gate)

    def user_gate_definition(self, linenum, txt):
        txt = txt.strip()
        gate_decl = QTRegEx.GATE_DECL.match(txt)
        gate_name = gate_decl.group(1)
        gate_params = gate_decl.group(2)
        gate_param_list = gate_params.split(',')
        gate_ops = QTRegEx.GATE_OPS.match(txt)
        gate_ops_raw_list = QTRegEx.GATE_OPS_LIST.findall(gate_ops.group(1))
        gate_ops_list = []
        for op_raw in gate_ops_raw_list:
            op_raw = op_raw.strip()
            op = QTRegEx.GATE_OP.match(op_raw).group(1)
            op_params = QTRegEx.GATE_OP_PARAMS.match(op_raw)
            if op_params:
                op_param_list = op_params.group(1).split(',')
            else:
                op_param_list = None
            op_regs = QTRegEx.GATE_OP_REGS.match(op_raw)
            if op_regs:
                op_reg_list = op_regs.group(1).split(',')
            else:
                op_reg_list = None
            gate_ops_list.append({'op': op,
                                  'op_param_list': op_param_list,
                                  'op_reg_list': op_reg_list})
        gate = {'source': txt, 'linenum': linenum, 'gate_name': gate_name,
                'gate_param_list': gate_param_list,
                'gate_ops_raw_list': gate_ops_raw_list,
                'gate_ops_list': gate_ops_list}
        self.append_user_gate(gate)

    def translate(self):
        seen_noncomment = False
        parsing_gate = False
        gate_def = ''
        gate_start_line = None
        gate_start_linenum = None
        seen_open_curly = False
        i = 1
        for line in self.qasmsourcelines:

            astElement = None
            line = line.strip()

            if parsing_gate:
                if not seen_open_curly:
                    x = QTRegEx.START_CURLY.search(line)
                    if not x:
                        raise Qasm_Gate_Missing_Open_Curly(i, gate_start_line,
                                                           gate_start_linenum)
                    else:
                        seen_open_curly = True
                        gate_def = gate_def + line + ' '
                        x = QTRegEx.END_CURLY.search(line)
                        if x:
                            self.user_gate_definition(
                                gate_start_linenum, gate_def)
                            parsing_gate = False
                            gate_def = ''
                            gate_start_line = None
                            gate_start_linenum = None
                            seen_open_curly = False
                else:
                    gate_def = gate_def + line + ' '
                    x = QTRegEx.END_CURLY.search(line)
                    if x:
                        self.user_gate_definition(gate_start_linenum, gate_def)
                        parsing_gate = False
                        gate_def = ''
                        gate_start_line = None
                        gate_start_linenum = None
                        seen_open_curly = False

                i = i + 1
                continue

            astElement = ASTElementUnknown(i, line)
            astType = ASTType.astType(line)
            if astType == ASTType.BLANK:
                i = i + 1
                continue
            if not seen_noncomment and astType != ASTType.COMMENT:
                if astType == ASTType.DECLARATION_QASM_2_0:
                    seen_noncomment = True
                else:
                    raise Qasm_Declaration_Absent_Exception(i, line)

            # Now step thru types
            if astType == ASTType.COMMENT:
                astElement = ASTElementComment(i, line)
            elif astType == ASTType.DECLARATION_QASM_2_0:
                astElement = ASTElementDeclarationQasm2_0(i, line)
            if astType == ASTType.INCLUDE:
                astElement = ASTElementInclude(i, line)
            elif astType == ASTType.QREG:
                astElement = ASTElementQReg(i, line)
            elif astType == ASTType.CREG:
                astElement = ASTElementCReg(i, line)
            elif astType == ASTType.MEASURE:
                astElement = ASTElementMeasure(i, line)
            elif astType == ASTType.BARRIER:
                astElement = ASTElementBarrier(i, line)

            elif astType == ASTType.GATE:
                parsing_gate = True
                gate_start_line = line
                gate_start_linenum = i
                gate_def = line + ' '
                x = QTRegEx.START_CURLY.search(line)
                if x:
                    seen_open_curly = True
                    x = QTRegEx.END_CURLY.search(line)
                    if x:
                        self.user_gate_definition(gate_start_linenum, gate_def)
                        parsing_gate = False
                        gate_def = ''
                        gate_start_line = None
                        gate_start_linenum = None
                        seen_open_curly = False
                i = i + 1
                continue

            elif astType == ASTType.OP:
                astElement = ASTElementOp(i, line)
            if type(astElement) is ASTElementUnknown and self.no_unknown:
                raise Qasm_Unknown_Element(i, line)
            self.append_ast(astElement.out())
            i = i + 1

        if parsing_gate:
            raise Qasm_Incomplete_Gate(i, gate_start_line, gate_start_linenum)

    def get_translation(self):
        return self.translation


class Qasm_Error(Exception):
    """Base class for Qasm exceptions"""

    def __init__(self, linenum, line):
        self.linenum = linenum
        self.line = line
        self.message = "Qasm_Error"
        self.errcode = 10

    def errpacket(self):
        ex = {'message': self.message,
              'linenum': self.linenum,
              'line': self.line,
              'errcode': self.errcode
              }
        return ex


class Qasm_Declaration_Absent_Exception(Qasm_Error):
    """QASM2.0 Declaration not first non-blank non-comment line"""

    def __init__(self, linenum, line):
        super(Qasm_Declaration_Absent_Exception, self).__init__(linenum, line)
        self.message = "QASM2.0 Declaration not first non-blank non-comment line"
        self.errcode = 20


class Qasm_Unknown_Element(Qasm_Error):
    """Unknown element"""

    def __init__(self, linenum, line):
        super(Qasm_Unknown_Element, self).__init__(linenum, line)
        self.message = "Unknown element"
        self.errcode = 30


class Qasm_Incomplete_Gate(Qasm_Error):
    """Gate definition incomplete"""

    def __init__(self, linenum, line, start_linenum):
        super(Qasm_Incomplete_Gate, self).__init__(linenum, line)
        self.start_linenum = start_linenum
        self.message = "Gate definition incomplete"
        self.errcode = 40

    def errpacket(self):
        ex = {'message': self.message,
              'linenum': self.linenum,
              'line': self.line,
              'start_linenum': self.start_linenum,
              'errcode': self.errcode
              }
        return ex


class Qasm_Gate_Missing_Open_Curly(Qasm_Error):
    """Gate definition incomplete"""

    def __init__(self, linenum, line, start_linenum):
        super(Qasm_Gate_Missing_Open_Curly, self).__init__(linenum, line)
        self.start_linenum = start_linenum
        self.message = "Gate definition missing open curly brace"
        self.errcode = 40

    def errpacket(self):
        ex = {'message': self.message,
              'linenum': self.linenum,
              'line': self.line,
              'start_linenum': self.start_linenum,
              'errcode': self.errcode
              }
        return ex
