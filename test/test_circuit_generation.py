#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:03:20 2020

@author: jax
"""
import os
import unittest
import nuqasm2 as nq


class TestCircuitGeneration(unittest.TestCase):
    """Test nuqasm2 regressions"""

    include_path = os.getenv('NUQASM2_INCLUDE_PATH') + ':test/qasm_src'

    def _test_circ_qasm_file_raises(self, regression_name, expected_exception):
        """Factor to run translation and watch for exception"""
        from_file_path = 'test/qasm_src/' + regression_name + '.qasm'
        qt = nq.qasmast.QasmTranslator.fromFile(from_file_path,  #pylint: disable-msg=invalid-name
                                                include_path=self.include_path)
        with self.assertRaises(expected_exception):
            qt.translate()
            translated_ast = qt.get_translation()
            ast2circ = nq.Ast2Circ(nuq2_ast=translated_ast)
            ast2circ.translate()

    def test_unknown_op(self):
        """Test unknown op that can't be unrolled."""
        self._test_circ_qasm_file_raises("unknown_op", nq.Ast2CircOpNotFoundException)
