from .relation import QueryBody


class SetOperation(QueryBody):
    def __init__(self, line=None, pos=None):
        super(SetOperation, self).__init__(line, pos)

    def accept(self, visitor, context):
        visitor.visit_set_operation(self, context)

    # TODO: use class names to deduplicate __str__ methods

    def __repr__(self):
        return repr(self.__dict__)


class Except(SetOperation):
    def __init__(self, line=None, pos=None, left=None, right=None, distinct=None):
        super(Except, self).__init__(line, pos)
        self.left = left
        self.right = right
        self.distinct = distinct

    def accept(self, visitor, context):
        visitor.visit_except(self, context)

    def __str__(self):
        maybe_distinct = (" " + self.distinct) if self.distinct else ""
        return " EXCEPT{} ".format(maybe_distinct).join([str(self.left), str(self.right)])


class Intersect(SetOperation):
    def __init__(self, line=None, pos=None, relations=None, distinct=None):
        super(Intersect, self).__init__(line, pos)
        self.relations = relations
        self.distinct = distinct

    def accept(self, visitor, context):
        visitor.visit_intersect(self, context)

    def __str__(self):
        maybe_distinct = (" " + self.distinct) if self.distinct else ""
        return " INTERSECT{} ".format(maybe_distinct).join(self.relations)


class Union(SetOperation):
    def __init__(self, line=None, pos=None, relations=None, distinct=None):
        super(Union, self).__init__(line, pos)
        self.relations = relations
        self.distinct = distinct

    def accept(self, visitor, context):
        visitor.visit_union(self, context)

    def __str__(self):
        maybe_distinct = (" " + self.distinct) if self.distinct else ""
        return " UNION{} ".format(maybe_distinct).join(self.relations)
