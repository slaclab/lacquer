from . import Node


class Select(Node):
    def __init__(self, line=None, pos=None, distinct=None, select_items=None):
        super(Select, self).__init__(line, pos)
        self.distinct = distinct
        self.select_items = select_items

    def is_distinct(self):
        pass

    def accept(self, visitor, context):
        visitor.visit_select(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this)
            .add("distinct", distinct).add("selectItems", selectItems).omitNullValues().toString();
        """
        pass
