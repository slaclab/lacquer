from .node import Node


class SelectItem(Node):

    def __init__(self, line=None, pos=None):
        super(SelectItem, self).__init__(line, pos)


class AllColumns(SelectItem):
    def __init__(self, line=None, pos=None, prefix=None):
        super(AllColumns, self).__init__(line=line, pos=pos)
        self.prefix = prefix

    def accept(self, visitor, context):
        visitor.visit_all_columns(self, context)

    def __str__(self):
        return "%s*" % (self.prefix + ".") if self.prefix else ""


class SingleColumn(SelectItem):
    def __init__(self, line=None, pos=None, alias=None, expression=None):
        super(SingleColumn, self).__init__(line, pos)
        self.alias = alias
        self.expression = expression

    def accept(self, visitor, context):
        visitor.visit_single_column(self, context)

    def __str__(self):
        return str(self.expression) + (" " + self.alias) if self.alias else ""
