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

import unittest
import os

from lacquer import parser
from lacquer.formatter import format_sql
from lacquer.formatter import JsonNodeEncoder


class TestQueries(unittest.TestCase):

    def setUp(self):
        test_queries = []
        current_query = []
        with open(os.path.join(os.path.dirname(__file__), "queries.sql")) as queries:
            for line in queries.readlines():
                line = line[:-1]
                if not len(line.strip()):
                    continue
                if line.strip()[-1] == ";":
                    idx = line.rfind(";")
                    current_query.append(line[0:idx])
                    test_queries.append('\n'.join(current_query))
                    current_query = []
                else:
                    current_query.append(line)
        self.queries = test_queries

    def test_parse_queries(self):
        err = 0
        for query in self.queries:
            if query[:2] == "--":
                continue
            try:
                parser.parse(query, tracking=True)
            except SyntaxError as e:
                print("Error parsing query:")
                e.print_file_and_line(e)
                err +=1
        if err:
            self.fail("Encountered %d errors" % err)

    def test_format_queries(self):
        err = 0
        for query in self.queries:
            if query[:2] == "--":
                continue
            try:
                tree = parser.parse(query, tracking=True)
                format_sql(tree, 0)
            except Exception as e:
                err += 1
                print("\n\n")
                print(query)
                print("failed to format:\n" + str(tree))
                print(e)
                print("\n\n")
        if err:
            self.fail("Encountered %d errors" % err)

    def test_format_json(self):
        err = 0
        for query in self.queries:
            if query[:2] == "--":
                continue
            try:
                tree = parser.parse(query, tracking=True)
                JsonNodeEncoder(indent=4).encode(tree)
            except SyntaxError as e:
                err += 1
        if err:
            self.fail("Encountered %d errors" % err)


if __name__ == '__main__':
    unittest.main()
