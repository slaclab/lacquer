from .node import Node


class GroupBy(Node):
    def __init__(self, line=None, pos=None, distinct=None, grouping_elements=None):
        super(GroupBy, self).__init__(line, pos)
        self.distinct = distinct
        self.grouping_elements = grouping_elements


class GroupingElement(Node):
    def __init__(self, line=None, pos=None):
        super(GroupingElement, self).__init__(line, pos)

    # def enumerate_grouping_sets(self):
    #     pass


class GroupingSets(GroupingElement):
    def __init__(self, line=None, pos=None, sets=None):
        super(GroupingSets, self).__init__(line, pos)
        self.sets = sets

    # def enumerate_grouping_sets(self):
    #     pass

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("sets", sets).toString();
    #     """


class SimpleGroupBy(GroupingElement):
    def __init__(self, line=None, pos=None, columns=None):
        super(SimpleGroupBy, self).__init__(line, pos)
        self.columns = columns

    # def enumerate_grouping_sets(self):
    #     pass

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("columns", columns).toString();
    #     """
