from .node import Node
from future.types import newint


class Literal(Node):
    def __init__(self, line=None, pos=None):
        super(Literal, self).__init__(line, pos)


class IntervalLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None, sign=None, start_field=None, end_field=None):
        super(IntervalLiteral, self).__init__(line, pos)
        self.value = value
        self.sign = sign
        self.start_field = start_field
        self.end_field = end_field

    # def is_year_to_month(self):
    #     pass

    def accept(self, visitor, context):
        return visitor.visit_interval_literal(self, context)

    
class TimestampLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None):
        super(TimestampLiteral, self).__init__(line, pos)
        self.value = value

    def accept(self, visitor, context):
        return visitor.visit_timestamp_literal(self, context)


class NullLiteral(Literal):
    def __init__(self, line=None, pos=None):
        super(NullLiteral, self).__init__(line, pos)

    def accept(self, visitor, context):
        return visitor.visit_null_literal(self, context)


class DoubleLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None):
        super(DoubleLiteral, self).__init__(line, pos)
        self.value = float(value)

    def accept(self, visitor, context):
        return visitor.visit_double_literal(self, context)


# class GenericLiteral(Literal):
#     def __init__(self, line=None, pos=None, type=None, value=None):
#         super(GenericLiteral, self).__init__(line, pos)
#         self.type = type
#         self.value = value
#
#     def accept(self, visitor, context):
#         return visitor.visit_generic_literal(self, context)


class StringLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None):
        super(StringLiteral, self).__init__(line, pos)
        self.value = value

    def accept(self, visitor, context):
        return visitor.visit_string_literal(self, context)


class TimeLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None):
        super(TimeLiteral, self).__init__(line, pos)
        self.value = value

    def accept(self, visitor, context):
        return visitor.visit_time_literal(self, context)

    def __str__(self):
        return "TIME '%s'" % self.value


class LongLiteral(Literal):
    def __init__(self, line=None, pos=None, value=None):
        super(LongLiteral, self).__init__(line, pos)
        self.value = newint(value)

    def accept(self, visitor, context):
        return visitor.visit_long_literal(self, context)

    def __str__(self):
        return self.value


class BooleanLiteral(Literal):
    """
    {'type': BooleanLiteral, 'name': TRUE_LITERAL = new  BooleanLiteral(null, "true"), 'order': 0}
    {'type': BooleanLiteral, 'name': FALSE_LITERAL = new  BooleanLiteral(null, "false"), 'order': 1}
    """
    def __init__(self, line=None, pos=None, value=None):
        super(BooleanLiteral, self).__init__(line, pos)
        self.value = value.lower() == "true"

    def accept(self, visitor, context):
        return visitor.visit_boolean_literal(self, context)
