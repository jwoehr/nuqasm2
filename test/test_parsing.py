#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:03:20 2020

@author: jax
"""
import io
import os
import unittest
import nuqasm2 as nq


class TestParsing(unittest.TestCase):

    include_path = os.getenv('NUQASM2_INCLUDE_PATH', '.')
    
    def test_test(self):
        self.assertFalse(nq.qasmast.ASTType.UNKNOWN.value)

    def _test_circ_qasm_file_compare(self, regression_name):
        self.maxDiff = None
        from_file_path = 'test/qasm_src/' + regression_name + '.qasm'
        validation_file_path = 'test/validation_output/' + regression_name + '.output.txt'
        qt = nq.qasmast.QasmTranslator.fromFile(from_file_path,
                                                include_path=self.include_path)
        qt.translate()
        translated_ast = qt.get_translation()
        ast2circ = nq.Ast2Circ(nuq2_ast=translated_ast)
        circ = ast2circ.translate().circuit
        qasm = circ.qasm()
        qasm_list_raw=qasm.split('\n')
        qasm_list = []
        for line in qasm_list_raw:
            qasm_list.append(line + '\n')
        validation_file = io.open(validation_file_path)
        self.assertListEqual(qasm_list, list(validation_file))
        validation_file.close()

    def test_constant_parm_to_gate_op(self):
        self._test_circ_qasm_file_compare('constant_parm_to_gate_op')

    def test_no_space_before_curly_gatedef(self):
        self._test_circ_qasm_file_compare('no_space_before_curly_gatedef')
