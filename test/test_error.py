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

from lacquer import parser


class ErrorTests(unittest.TestCase):

    def test_error_message(self):
        try:
            bad_sql = "select foo(selcet bar from b)"
            parser.parse(bad_sql)
        except SyntaxError as e:
            err_pos = bad_sql.find("bar")
            self.assertEqual("Syntax error at position %d (bar)" % err_pos, e.msg)

        try:
            bad_sql = "select foo\n\n\n(selcet bar from b)"
            parser.parse(bad_sql)
        except SyntaxError as e:
            err_pos = bad_sql.split("\n")[3].find("bar")
            self.assertEqual("Syntax error at position %d (bar)" % err_pos, e.msg)

if __name__ == '__main__':
    unittest.main()
