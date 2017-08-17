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

from lacquer import parser, expression_parser
from lacquer.tree import *

negative = ArithmeticUnaryExpression.negative
positive = ArithmeticUnaryExpression.positive


class PrestoTests(unittest.TestCase):

    def test_double(self):
        assert_expression("123.", DoubleLiteral(value="123"))
        assert_expression("123.0", DoubleLiteral(value="123"))
        assert_expression(".5", DoubleLiteral(value=".5"))
        assert_expression("123.5", DoubleLiteral(value="123.5"))

        assert_expression("123E7", DoubleLiteral(value="123E7"))
        assert_expression("123.E7", DoubleLiteral(value="123E7"))
        assert_expression("123.0E7", DoubleLiteral(value="123E7"))
        assert_expression("123E+7", DoubleLiteral(value="123E7"))
        assert_expression("123E-7", DoubleLiteral(value="123E-7"))

        assert_expression("123.456E7", DoubleLiteral(value="123.456E7"))
        assert_expression("123.456E+7", DoubleLiteral(value="123.456E7"))
        assert_expression("123.456E-7", DoubleLiteral(value="123.456E-7"))

        assert_expression(".4E42", DoubleLiteral(value=".4E42"))
        assert_expression(".4E+42", DoubleLiteral(value=".4E42"))
        assert_expression(".4E-42", DoubleLiteral(value=".4E-42"))

    def test_cast(self):
        assert_expression("CAST(a AS BIGINT)",
                          Cast(expression=QualifiedNameReference(name=QualifiedName.of("a")),
                               data_type="BIGINT", safe=False))
        assert_expression("CAST(a AS VARCHAR(2))",
                          Cast(expression=QualifiedNameReference(name=QualifiedName.of("a")),
                               data_type="VARCHAR(2)", safe=False))
        assert_expression("CAST(a AS NUMBER(2,3))",
                          Cast(expression=QualifiedNameReference(name=QualifiedName.of("a")),
                               data_type="NUMBER(2,3)", safe=False))
        assert_expression("CAST(a AS FOO(BAR))",
                          Cast(expression=QualifiedNameReference(name=QualifiedName.of("a")),
                               data_type="FOO(BAR)", safe=False))

    def test_between(self):
        assert_expression(
            "1 BETWEEN 2 AND 3",
            BetweenPredicate(value=LongLiteral(value="1"),
                             min=LongLiteral(value="2"),
                             max=LongLiteral(value="3")))
        assert_expression(
            "1 NOT BETWEEN 2 AND 3",
            NotExpression(value=BetweenPredicate(value=LongLiteral(value="1"),
                                                 min=LongLiteral(value="2"),
                                                 max=LongLiteral(value="3"))))

    def test_associativity(self):
        assert_expression(
            "1 AND 2 OR 3",
            LogicalBinaryExpression(type="OR",
                                    left=LogicalBinaryExpression(type="AND",
                                                                 left=LongLiteral(value="1"),
                                                                 right=LongLiteral(value="2")),
                                    right=LongLiteral(value="3")))

        assert_expression(
            "1 OR 2 AND 3",
            LogicalBinaryExpression(type="OR",
                                    left=LongLiteral(value="1"),
                                    right=LogicalBinaryExpression(type="AND",
                                                                  left=LongLiteral(value="2"),
                                                                  right=LongLiteral(value="3"))))

        assert_expression(
            "NOT 1 AND 2",
            LogicalBinaryExpression(type="AND",
                                    left=NotExpression(value=LongLiteral(value="1")),
                                    right=LongLiteral(value="2")))

        assert_expression(
            "NOT 1 OR 2",
            LogicalBinaryExpression(type="OR",
                                    left=NotExpression(value=LongLiteral(value="1")),
                                    right=LongLiteral(value="2")))

        assert_expression(
            "-1 + 2", ArithmeticBinaryExpression(type="+",
                                                 left=negative(LongLiteral(value="1")),
                                                 right=LongLiteral(value="2")))

        assert_expression(
            "-(1 + 2)", negative(ArithmeticBinaryExpression(type="+",
                                                            left=LongLiteral(value="1"),
                                                            right=LongLiteral(value="2"))))

        assert_expression(
            "1 - 2 - 3",
            ArithmeticBinaryExpression(type="-",
                                       left=ArithmeticBinaryExpression(
                                           type="-",
                                           left=LongLiteral(value="1"),
                                           right=LongLiteral(value="2")),
                                       right=LongLiteral(value="3")))

        assert_expression(
            "1 / 2 / 3",
            ArithmeticBinaryExpression(type="/",
                                       left=ArithmeticBinaryExpression(
                                           type="/",
                                           left=LongLiteral(value="1"),
                                           right=LongLiteral(value="2")),
                                       right=LongLiteral(value="3")))
        assert_expression(
            "1 + 2 * 3",
            ArithmeticBinaryExpression(type="+",
                                       left=LongLiteral(value="1"),
                                       right=ArithmeticBinaryExpression(
                                           type="*",
                                           left=LongLiteral(value="2"),
                                           right=LongLiteral(value="3"))))

    def test_arithmetic_unary(self):
        assert_expression("9", LongLiteral(value="9"))

        assert_expression("+9", positive(LongLiteral(value="9")))
        assert_expression("+ 9", positive(LongLiteral(value="9")))

        # TODO: Fix the following expressions so they work!
        # assert_expression("++9", positive(positive(LongLiteral(value="9"))))
        # assert_expression("+ +9", positive(positive(LongLiteral(value="9"))))
        # assert_expression("+ + 9", positive(positive(LongLiteral(value="9"))))
        #
        # assert_expression("+++9", positive(positive(positive(LongLiteral(value="9")))))
        # assert_expression("+ + +9", positive(positive(positive(LongLiteral(value="9")))))
        # assert_expression("+ + + 9", positive(positive(positive(LongLiteral(value="9")))))
        #
        assert_expression("-9", negative(LongLiteral(value="9")))
        assert_expression("- 9", negative(LongLiteral(value="9")))
        #
        # assert_expression("- + 9", negative(positive(LongLiteral(value="9"))))
        # assert_expression("-+9", negative(positive(LongLiteral(value="9"))))
        #
        # assert_expression("+ - + 9", positive(negative(positive(LongLiteral(value="9")))))
        # assert_expression("+-+9", positive(negative(positive(LongLiteral(value="9")))))
        #
        # assert_expression("- -9", negative(negative(LongLiteral(value="9"))))
        # assert_expression("- - 9", negative(negative(LongLiteral(value="9"))))
        #
        # assert_expression("- + - + 9",
        #                   negative(positive(negative(positive(LongLiteral(value="9"))))))
        # assert_expression("-+-+9",
        #                   negative(positive(negative(positive(LongLiteral(value="9"))))))
        #
        # assert_expression(
        #          "+ - + - + 9",
        #          positive(negative(positive(negative(positive(LongLiteral(value="9")))))))
        # assert_expression(
        #         "+-+-+9",
        #         positive(negative(positive(negative(positive(LongLiteral(value="9")))))))
        #
        # assert_expression("- - -9", negative(negative(negative(LongLiteral(value="9")))))
        # assert_expression("- - - 9", negative(negative(negative(LongLiteral(value="9")))))

    def test_current_timestamp(self):
        assert_expression("CURRENT_TIMESTAMP", CurrentTime(type="CURRENT_TIMESTAMP"))

    def test_double_in_query(self):
        assert_statement("SELECT 123.456E7 FROM DUAL",
                         simple_query(select_list(DoubleLiteral(value="123.456E7")),
                                      Table(name=QualifiedName.of("DUAL"))
                                      )
                         )

    def test_intersect(self):
        assert_statement(
            "SELECT 123 INTERSECT DISTINCT SELECT 456 INTERSECT ALL SELECT 789",
            Query(query_body=Intersect(
                relations=[
                    Intersect(relations=[_select(123), _select(456)], distinct=True),
                    _select(789)
                ], distinct=False)
            )
        )

        assert_statement(
            "SELECT 123 intersect distinct SELECT 456 INTERSECT all SELECT 789",
            Query(query_body=Intersect(
                relations=[
                    Intersect(relations=[_select(123), _select(456)], distinct=True),
                    _select(789)
                ], distinct=False)
            )
        )

    def test_union(self):
        assert_statement(
            "SELECT 123 UNION SELECT 456 union ALL SELECT 789",
            Query(query_body=Union(
                relations=[
                    Union(relations=[_select(123), _select(456)], distinct=True),
                    _select(789)
                ], distinct=False)
            )
        )

        assert_statement(
            "SELECT 123 UNION distinct SELECT 456 union DISTINCT SELECT 789",
            Query(query_body=Union(
                relations=[
                    Union(relations=[_select(123), _select(456)], distinct=True),
                    _select(789)
                ], distinct=True)
            )
        )

    def test_group_by(self):
        assert_statement("SELECT * FROM table1 GROUP BY a",
                         Query(
                             query_body=QuerySpecification(
                                 select=select_list_with_items(AllColumns()),
                                 from_=Table(name=QualifiedName.of("table1")),
                                 group_by=SimpleGroupBy(
                                     columns=[QualifiedNameReference(name=QualifiedName.of("a"))]
                                 )
                             )),
                         )

        assert_statement("SELECT * FROM table1 GROUP BY a, b",
                         Query(
                             query_body=QuerySpecification(
                                 select=select_list_with_items(AllColumns()),
                                 from_=Table(name=QualifiedName.of("table1")),
                                 group_by=SimpleGroupBy(
                                     columns=[QualifiedNameReference(name=QualifiedName.of("a")),
                                              QualifiedNameReference(name=QualifiedName.of("b"))]
                                 )
                             )),
                         )

    def test_implicit_join(self):
        assert_statement("SELECT * FROM a, b",
                         simple_query(select_list_with_items(AllColumns()),
                                      Join(join_type="IMPLICIT",
                                           left=Table(name=QualifiedName.of("a")),
                                           right=Table(name=QualifiedName.of("b"))
                                           )
                                      )
                         )

    def test_join_precedence(self):
        assert_statement("SELECT * FROM a CROSS JOIN b LEFT JOIN c ON true",
                         simple_query(select_list_with_items(AllColumns()),
                                      Join(join_type="LEFT",
                                           left=Join(
                                                     join_type="CROSS",
                                                     left=Table(name=QualifiedName.of("a")),
                                                     right=Table(name=QualifiedName.of("b"))
                                           ),
                                           right=Table(name=QualifiedName.of("c")),
                                           criteria=JoinOn(BooleanLiteral.TRUE_LITERAL)
                                           )
                                      )
                         )

        assert_statement(
            "SELECT * FROM a CROSS JOIN b NATURAL JOIN c CROSS JOIN d NATURAL JOIN e",
            simple_query(
                select_list_with_items(AllColumns()),
                Join(join_type="INNER",
                     left=Join(join_type="CROSS",
                               left=Join(join_type="INNER",
                                         left=Join(join_type="CROSS",
                                                   left=Table(name=QualifiedName.of("a")),
                                                   right=Table(name=QualifiedName.of("b"))),
                                         right=Table(name=QualifiedName.of("c")),
                                         criteria=NaturalJoin()),
                               right=Table(name=QualifiedName.of("d"))
                               ),
                     right=Table(name=QualifiedName.of("e")),
                     criteria=NaturalJoin()))
        )

    def test_non_reserved(self):
        assert_statement(
            "SELECT zone FROM t",
            simple_query(select_list(QualifiedNameReference(name=QualifiedName.of("zone"))),
                         Table(name=QualifiedName.of("t"))
                         )
        )

    def test_where(self):
        assert_statement(
            'select x from foo where bar = 3',
            simple_query(
                select_list(QualifiedNameReference(name=QualifiedName.of("x"))),
                Table(name=QualifiedName.of("foo")),
                where=ComparisonExpression(
                    type='=',
                    left=QualifiedNameReference(name=QualifiedName.of("bar")),
                    right=LongLiteral(value=3)
                 )
            )
        )

        assert_statement(
            'select x from foo where (bar = 3)',
            simple_query(
                select_list(QualifiedNameReference(name=QualifiedName.of("x"))),
                Table(name=QualifiedName.of("foo")),
                where=ComparisonExpression(
                    type='=',
                    left=QualifiedNameReference(name=QualifiedName.of("bar")),
                    right=LongLiteral(value=3)
                 )
            )
        )

def _select(x):
    return parser.parse("select %s" % x).query_body


def assert_statement(expr, expected):
    assert_parsed(expr, expected, parser.parse(expr))


def assert_expression(expr, expected):
    assert_parsed(expr, expected, expression_parser.parse(expr))


def assert_parsed(input, expected, parsed):
    template = ("expected:\n\n{input}\n\n"
                "to parse as:\n\n{expected}\n\n"
                "but found:\n\n{parsed}\n")
    msg = template.format(input=input,
                          expected=repr(expected),
                          parsed=repr(parsed))
    assert parsed == expected, msg


def select_list(*args):
    return Select(select_items=[SingleColumn(expression=arg) for arg in args])


def select_list_with_items(*args):
    return Select(select_items=list(args))


def simple_query(select, from_=None, where=None):
    return Query(query_body=QuerySpecification(select=select, from_=from_, where=where))