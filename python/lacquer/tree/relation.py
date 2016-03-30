from .node import Node


class Relation(Node):
    def __init__(self, line=None, pos=None):
        super(Relation, self).__init__(line, pos)

    def accept(self, visitor, context):
        visitor.visit_relation(self, context)


class AliasedRelation(Relation):
    def __init__(self, line=None, pos=None, relation=None, alias=None, column_names=None):
        super(AliasedRelation, self).__init__(line, pos)
        self.relation = relation
        self.alias = alias
        self.column_names = column_names

    def accept(self, visitor, context):
        visitor.visit_aliased_relation(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).
            add("relation", relation).add("alias", alias).add("columnNames", columnNames).omitNullValues().toString();
        """
        pass


class Join(Relation):
    def __init__(self, line=None, pos=None, type=None, left=None, right=None, criteria=None):
        super(Join, self).__init__(line, pos)
        self.type = type
        self.left = left
        self.right = right
        self.criteria = criteria

    def accept(self, visitor, context):
        visitor.visit_join(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).add("type", type).
            add("left", left).add("right", right).add("criteria", criteria).omitNullValues().toString();
        """
        pass


class QueryBody(Relation):
    def __init__(self, line=None, pos=None):
        super(QueryBody, self).__init__(line, pos)

    def accept(self, visitor, context):
        visitor.visit_query_body(self, context)


class Unnest(Relation):
    def __init__(self, line=None, pos=None, expressions=None, with_ordinality=None):
        super(Unnest, self).__init__(line, pos)
        self.expressions = expressions
        self.with_ordinality = with_ordinality

    def is_with_ordinality(self):
        pass

    def accept(self, visitor, context):
        visitor.visit_unnest(self, context)

    def __str__(self):
        """
        String result = "UNNEST(" + Joiner.on(", ").join(expressions) + ")";
        if (withOrdinality) {
            result += " WITH ORDINALITY";
        }
        return result;
        """
        pass
