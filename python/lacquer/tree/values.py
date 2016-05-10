from .relation import QueryBody


class Values(QueryBody):
    def __init__(self, line=None, pos=None, rows=None):
        super(Values, self).__init__(line, pos)
        self.rows = rows

    def accept(self, visitor, context):
        return visitor.visit_values(self, context)

    def __str__(self):
        return "(" + ", ".join(self.rows or []) + ")"
