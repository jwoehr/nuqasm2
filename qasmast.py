"""
qasmast.py
Classes to implement qasm2 translation to python data structures
Working from _Open Quantum Assembly Language_
https://arxiv.org/pdf/1707.03429.pdf
jack j. woehr jwoehr@softwoehr.com po box 51 golden co 80402-0051
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
from enum import Enum
import re

class ASTType(Enum):
    COMMENT = 1
    QREG = 2
    CREG = 3
    UNKNOWN = 0

    @classmethod
    def astType(cls, txt):
        astType = cls.UNKNOWN
        x = re.search("^\s*//", txt)
        if x:
            astType = cls.COMMENT
        return astType

class ASTElement():
    def __init__(self, linenum, ast_type, source, text):
        self.linenum = linenum
        self.ast_type = ast_type
        self.source = source
        self.text = text
        
    def out(self):
        return {'linenum': self.linenum, 'type': self.ast_type, 'source': self.source, 'text': self.text}

class ASTElementUnknown(ASTElement):
    def __init__(self, linenum, source, text):
        super(ASTElementUnknown, self).__init__(linenum, ASTType.UNKNOWN, source, text)
        
class ASTElementComment(ASTElement):
    def __init__(self, linenum, source, text):
        super(ASTElementComment, self).__init__(linenum, ASTType.COMMENT, source, text)

class QasmTranslation():

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

    def appendAST(self, text):
        self.translation['ast'].append(text)

    def translate(self):
        i=1
        for line in self.qasmsourcelines:
            astElement = ASTElementUnknown(i, line, line)
            astType = ASTType.astType(line)
            if astType == ASTType.COMMENT:
                astElement = ASTElementComment(i, line, line)
            self.appendAST(astElement.out())
            i=i+1

    def get_translation(self):
        return self.translation
