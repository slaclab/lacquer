from .node import Node


class SortItem(Node):
    def __init__(self, line=None, pos=None, sort_key=None, ordering=None, null_ordering=None):
        super(SortItem, self).__init__(line, pos)
        self.sort_key = sort_key
        self.ordering = ordering
        self.null_ordering = null_ordering

    def accept(self, visitor, context):
        visitor.visit_sort_item(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).add("sortKey", sortKey)
            .add("ordering", ordering).add("nullOrdering", nullOrdering).toString();
        """
        pass
