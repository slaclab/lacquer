import unittest
from lacquer.tree import *

from lacquer.parsers.parser import parser, expression_parser

negative = ArithmeticUnaryExpression.negative
positive = ArithmeticUnaryExpression.positive


class PrestoTests(unittest.TestCase):

    def test_between(self):
        assert_expression("1 BETWEEN 2 AND 3",
                          BetweenPredicate(value=LongLiteral(value="1"),
                                           min=LongLiteral(value="2"), max=LongLiteral(value="3")))
        assert_expression("1 NOT BETWEEN 2 AND 3",
                          NotExpression(value=
                                        BetweenPredicate(value=LongLiteral(value="1"),
                                                         min=LongLiteral(value="2"), max=LongLiteral(value="3"))))

    def test_associativity(self):
        assert_expression("1 AND 2 OR 3",
                          LogicalBinaryExpression(type="OR",
                                                  left=LogicalBinaryExpression(type="AND",
                                                                               left=LongLiteral(value="1"),
                                                                               right=LongLiteral(
                                                                                   value="2")),
                                                  right=LongLiteral(value="3")))

        assert_expression("1 OR 2 AND 3",
                          LogicalBinaryExpression(type="OR",
                                                  left=LongLiteral(value="1"),
                                                  right=LogicalBinaryExpression(type="AND",
                                                                                left=LongLiteral(
                                                                                    value="2"),
                                                                                right=LongLiteral(
                                                                                    value="3"))))

        assert_expression("NOT 1 AND 2",
                          LogicalBinaryExpression(type="AND",
                                                  left=NotExpression(value=LongLiteral(value="1")),
                                                  right=LongLiteral(value="2")))

        assert_expression("NOT 1 OR 2",
                          LogicalBinaryExpression(type="OR",
                                                  left=NotExpression(value=LongLiteral(value="1")),
                                                  right=LongLiteral(value="2")))

        assert_expression("-1 + 2", ArithmeticBinaryExpression(type="+",
                                                               left=negative(LongLiteral(value="1")),
                                                               right=LongLiteral(value="2")))

        assert_expression("-(1 + 2)", negative(ArithmeticBinaryExpression(type="+",
                                                                left=LongLiteral(value="1"),
                                                                right=LongLiteral(value="2"))))

        assert_expression("1 - 2 - 3",
                          ArithmeticBinaryExpression(type="-",
                                                     left=ArithmeticBinaryExpression(type="-",
                                                                                     left=LongLiteral(
                                                                                         value="1"),
                                                                                     right=LongLiteral(
                                                                                         value="2")),
                                                     right=LongLiteral(value="3")))

        assert_expression("1 / 2 / 3",
                          ArithmeticBinaryExpression(type="/",
                                                     left=ArithmeticBinaryExpression(type="/",
                                                                                     left=LongLiteral(
                                                                                         value="1"),
                                                                                     right=LongLiteral(
                                                                                         value="2")),
                                                     right=LongLiteral(value="3")))
        assert_expression("1 + 2 * 3",
                          ArithmeticBinaryExpression(type="+",
                                                     left=LongLiteral(value="1"),
                                                     right=ArithmeticBinaryExpression(type="*",
                                                                                      left=LongLiteral(value="2"),
                                                                                      right=LongLiteral(value="3")))
                          )

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
        # assert_expression("- + - + 9", negative(positive(negative(positive(LongLiteral(value="9"))))))
        # assert_expression("-+-+9", negative(positive(negative(positive(LongLiteral(value="9"))))))
        #
        # assert_expression("+ - + - + 9", positive(negative(positive(negative(positive(LongLiteral(value="9")))))))
        # assert_expression("+-+-+9", positive(negative(positive(negative(positive(LongLiteral(value="9")))))))
        #
        # assert_expression("- - -9", negative(negative(negative(LongLiteral(value="9")))))
        # assert_expression("- - - 9", negative(negative(negative(LongLiteral(value="9")))))

    def test_current_timestamp(self):
        assert_expression("CURRENT_TIMESTAMP", CurrentTime(type="CURRENT_TIMESTAMP"))

    def test_intersect(self):
        assert_statement(
            "SELECT 123 INTERSECT DISTINCT SELECT 123 INTERSECT ALL SELECT 123",
            Query(query_body=Intersect(
                relations=[
                    Intersect(relations=[create_select_123(), create_select_123()], distinct=True),
                    create_select_123()
                ], distinct=False)
            )
        )

    def test_double_in_query(self):
        assert_statement("SELECT 123.456E7 FROM DUAL",
                         simple_query(select_list(DoubleLiteral(value="123.456E7")),
                                      Table(name=QualifiedName.of("DUAL"))
                                      )
                         )


def create_select_123():
    return parser.parse("select 123").query_body


def assert_statement(expr, expected):
    assert_parsed(expr, expected, parser.parse(expr))


def assert_expression(expr, expected):
    assert_parsed(expr, expected, expression_parser.parse(expr))


def assert_parsed(input, expected, parsed):
    if parsed != expected:
        msg = "expected input:\n\n{input}\n\nto parse as:\n\n{expected}\n\nbut found:\n\n{parsed}\n"
        print(msg.format(input=input, expected=repr(expected), parsed=repr(parsed)))


def select_list(*args):
    return Select(select_items=[SingleColumn(expression=arg) for arg in args])


def simple_query(select, from_=None):
    return Query(query_body=QuerySpecification(select=select, from_=from_))