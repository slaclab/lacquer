from .node import Node


class ExplainOption(Node):
    def __init__(self, line=None, pos=None):
        super(ExplainOption, self).__init__(line, pos)

    def accept(self, visitor, context):
        visitor.visit_explain_option(self, context)


class ExplainType(ExplainOption):
    def __init__(self, line=None, pos=None, type=None):
        super(ExplainType, self).__init__(line, pos)
        self.type = type

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("type", type).toString();
    #     """


class ExplainFormat(ExplainOption):
    def __init__(self, line=None, pos=None, type=None):
        super(ExplainFormat, self).__init__(line, pos)
        self.type = type

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("type", type).toString();
    #     """

