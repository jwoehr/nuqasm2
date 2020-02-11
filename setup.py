#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 12:04:26 2019

@author: jax
"""
from setuptools import setup, find_packages

setup(
    name="nuqasm2",
    version="0.3",
    description="Compile OPENQASM2 to QuantumCircuit",
    url="https://github.com/jwoehr/nuqasm2",
    author="Jack Woehr",
    author_email="jwoehr@softwoehr.com",
    install_requires=['qiskit-terra','numpy'],
    license="Apache 2.0",
    packages=find_packages(),
    # packages=['nuqasm2'],
    scripts=['scripts/nuqasm2'],
    zip_safe=False
    # ,
    # ext_modules=cythonize(["nuqasm2/qasmast.pyx", "nuqasm2/ast2circ.pyx"],
    #                       compiler_directives={'language_level': "3"})
)
