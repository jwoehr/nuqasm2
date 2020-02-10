#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 12:04:26 2019

@author: jax
"""
import sys
from setuptools import setup, find_packages
try:
    from Cython.Build import cythonize
except ImportError:
    import subprocess
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'Cython>=0.27.1'])
    from Cython.Build import cythonize

setup(
    name="nuqasm2",
    version="0.3",
    description="Compile OPENQASM2 to QuantumCircuit",
    url="https://github.com/jwoehr/nuqasm2",
    author="Jack Woehr",
    author_email="jwoehr@softwoehr.com",
    license="Apache 2.0",
    packages=find_packages(),
    # packages=['nuqasm2'],
    scripts=['scripts/nuqasm2'],
    zip_safe=False
    # ,
    # ext_modules=cythonize(["nuqasm2/qasmast.pyx", "nuqasm2/ast2circ.pyx"],
    #                       compiler_directives={'language_level': "3"})
)
