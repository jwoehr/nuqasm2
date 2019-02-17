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
        x = re.search(r"^\s*//", source)
        if x:
            return cls.COMMENT
        x = re.search(r"^\s*include\s+\"\S+\"\s*;", source)
        if x:
            return cls.INCLUDE
        x = re.search(r"^\s*qreg\s+\S*\[\d+\]\s*;", source)
        if x:
            return cls.QREG
        x = re.search(r"^\s*creg\s+\S*\[\d+\]\s*;", source)
        if x:
            return cls.CREG
        x = re.search(r"^\s*measure\s+\S+\s+\-\>\s+\S+\s*;", source)
        if x:
            return cls.MEASURE
        x = re.search(r"^\s*barrier\s+.*;", source)
        if x:
            return cls.BARRIER
        x = re.search(r"^\s*\S+\s+\S+\[\d+\]\s*;", source)
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
        x = re.search(r".*\"(\S+)\"\s*;", source)
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
        x = re.match(r".*(\S+)\[(\d+)\].*", self.source)
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
        x = re.match(r".*(\S+)\[(\d+)\].*", self.source)
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
        x = re.match(r"^\s*measure\s+(\S+)\s+\-\>\s+(\S+)\s*;", self.source)
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
        x = re.findall(r"\S+\[\d+\]", self.source)
        self.reg_list = x[0].split(',')

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'reg_list': self.reg_list}


class ASTElementOp(ASTElement):
    """
    ASTElementOp
    An operator
    Knows linenum, ast_type, source, op, reg_list
    """

    def __init__(self, linenum, source):
        super(ASTElementOp, self).__init__(linenum, ASTType.OP, source)
        x = re.match(r"^\s*(\S+)\s+.*", self.source)
        self.op = x.group(1)
        x = re.findall(r"\S+\[\d+\]", self.source)
        self.reg_list = x[0].split(',')

    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
                'source': self.source, 'op': self.op, 'reg_list': self.reg_list}


class QasmTranslator():

    def __init__(self, qasmsourcelines, filepath=None, datetime=None):
        self.qasmsourcelines = qasmsourcelines
        self.translation = {
            'filepath': filepath, 'datetime': datetime, 'source': qasmsourcelines, 'ast': []}

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

    def translate(self):
        seen_noncomment = False
        i = 1
        for line in self.qasmsourcelines:
            line = line.strip()
            astElement = ASTElementUnknown(i, line)
            astType = ASTType.astType(line)
            if astType == ASTType.BLANK:
                i = i + 1
                continue
            if not seen_noncomment and astType != ASTType.COMMENT:
                if astType == ASTType.DECLARATION_QASM_2_0:
                    seen_noncomment = True
                else:
                    raise Qasm_Declaration_Absent_Exception()

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
            elif astType == ASTType.OP:
                astElement = ASTElementOp(i, line)
            self.append_ast(astElement.out())
            i = i + 1

    def get_translation(self):
        return self.translation


class Qasm_Error(Exception):
    """Base class for Qasm exceptions"""
    pass


class Qasm_Declaration_Absent_Exception(Qasm_Error):
    """QASM2.0 Declaration not first non-blank non-comment line"""
    pass
