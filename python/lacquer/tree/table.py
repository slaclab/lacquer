from .relation import QueryBody


class Table(QueryBody):
    def __init__(self, line=None, pos=None, name=None):
        super(Table, self).__init__(line, pos)
        self.name = name

    def accept(self, visitor, context):
        visitor.visit_table(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).addValue(name).toString();
        """
        pass


class TableSubquery(QueryBody):
    def __init__(self, line=None, pos=None, query=None):
        super(TableSubquery, self).__init__(line, pos)
        self.query = query

    def accept(self, visitor, context):
        visitor.visit_table_subquery(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).addValue(query).toString();
        """
        pass
