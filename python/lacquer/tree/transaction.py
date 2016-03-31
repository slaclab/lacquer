from .node import Node


class TransactionMode(Node):
    def __init__(self, line=None, pos=None):
        super(TransactionMode, self).__init__(line, pos)

    def accept(self, visitor, context):
        visitor.visit_transaction_mode(self, context)


class Isolation(TransactionMode):
    def __init__(self, line=None, pos=None, level=None):
        super(Isolation, self).__init__(line, pos)
        self.level = level

    def accept(self, visitor, context):
        visitor.visit_isolation(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("level", level).toString();
    #     """


class TransactionAccessMode(TransactionMode):
    def __init__(self, line=None, pos=None, read_only=None):
        super(TransactionAccessMode, self).__init__(line, pos)
        self.read_only = read_only

    def is_read_only(self):
        pass

    def accept(self, visitor, context):
        visitor.visit_transaction_access_mode(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("readOnly", readOnly).toString();
    #     """
