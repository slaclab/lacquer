from .node import Node


class TableElement(Node):
    def __init__(self, line, pos, name, typedef):
        super(TableElement, self).__init__(line, pos)
        self.name = name
        self.typedef = typedef

    def accept(self, visitor, context):
        return visitor.visit_table_element(self, context)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).add("name", name).add("type", type).toString();
        """
        return " ".join([self.name, self.typedef])
