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
    COMMENT = 1
    QREG = 2
    CREG = 3
    BLANK = 1000
    DECLARATION_QASM_2_0 = 2000

    @classmethod
    def astType(cls, txt):
        txt.strip()
        if txt == '':
            return cls.BLANK
        if txt == "OPENQASM 2.0;":
            return cls.DECLARATION_QASM_2_0
        x = re.search(r"^\s*//", txt)
        if x:
            return cls.COMMENT
        x = re.search(r"^\s*qreg\s+\S*.*\[\d+\]\s*;", txt)
        if x:
            return cls.QREG
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
        super(ASTElementUnknown, self).__init__(linenum, ASTType.UNKNOWN, source)

class ASTElementComment(ASTElement):
    """
    ASTElementComment
    A programmer comment element
    Knows linenum, ast_type, source
    """
    def __init__(self, linenum, source):
        super(ASTElementComment, self).__init__(linenum, ASTType.COMMENT, source)
        
class ASTElementDeclarationQasm2_0(ASTElement):
    """
    ASTElementDeclarationQasm2_0
    Obligatory declaration
    Knows linenum, ast_type, source
    """
    def __init__(self, linenum, source):
        super(ASTElementDeclarationQasm2_0, self).__init__(linenum, ASTType.DECLARATION_QASM_2_0, source)
        
class ASTElementQReg(ASTElement):
    """
    ASTElementQReg
    A QReg declaration
    Knows linenum, ast_type, source, qreg_name, qreg_num
    """
    def __init__(self, linenum, source):
        super(ASTElementQReg, self).__init__(linenum, ASTType.QREG, source)
        x = re.search(r"\S\[\d+\]", source)
        self.qreg_name = 'x'
        self.qreg_num = 0
        
    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type,
        'source': self.source, 'qreg_name': self.qreg_name, 'qreg_num': self.qreg_num}

class QasmTranslator():

    def __init__(self, qasmsourcelines, filepath=None, datetime=None):
        self.qasmsourcelines=qasmsourcelines
        self.translation={'filepath':filepath, 'datetime':datetime, 'source':qasmsourcelines, 'ast': [] }

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
        i=1
        for line in self.qasmsourcelines:
            astElement = ASTElementUnknown(i, line)
            astType = ASTType.astType(line)
            if astType == ASTType.BLANK:
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
            elif astType == ASTType.QREG:
                astElement = ASTElementQReg(i, line)
            self.append_ast(astElement.out())
            i=i+1

    def get_translation(self):
        return self.translation

class Qasm_Error(Exception):
    """Base class for Qasm exceptions"""
    pass

class Qasm_Declaration_Absent_Exception(Qasm_Error):
    """QASM2.0 Declaration not first non-blank non-comment line"""
    pass