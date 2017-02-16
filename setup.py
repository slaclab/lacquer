# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
lacquer
-------

lacquer is a python port of Presto's SQL Parser.

Currently, it doesn't support all the same features as Presto's parser,
but it can parse most SELECT queries and produce the python-equivalent
syntax tree, as well as write the tree back out to SQL.

It was written for the `LSST project <http://lsst.org>`_ to enable
support for the Astronomical Data Query Language.

It has two dependencies, PLY and future.

It is tested with 2.7 and 3.5.

Links
`````
* `GitHub <http://github.com/slaclab/lacquer/>`_
* `development version
  <https://github.com/slaclab/lacquer/zipball/master#egg=lacquer-dev>`_

"""

import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('lacquer/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='lacquer',
    version=version,
    packages=find_packages(),
    url='http://github.com/slaclab/lacquer',
    license='Apache License 2.0',
    author='Brian Van Klaveren',
    author_email='bvan@slac.stanford.edu',
    description='A SQL Parser based on the parser in the presto project',
    long_description=__doc__,
    install_requires=[
        'ply',
        'future'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Compilers'
    ],
    zip_safe=False
)
