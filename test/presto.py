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


def assert_statement(expr, expected):
    assert_parsed(expr, expected, parser.parse(expression))


def assert_expression(expr, expected):
    assert_parsed(expr, expected, expression_parser.parse(expression))


def assert_parsed(input, expected, parsed):
    if parsed != expected:
        msg = "expected input:\n\n{input}\n\nto parse as:\n\n{expected}\n\nbut found:\n\n{parsed}\n"
        print(msg.format(input=input, expected=repr(expected), parsed=repr(parsed)))

