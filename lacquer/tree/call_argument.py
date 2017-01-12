from .node import Node


class CallArgument(Node):
    def __init__(self, line=None, pos=None, name=None, value=None):
        super(CallArgument, self).__init__(line, pos)
        self.name = name
        self.value = value

    def accept(self, visitor, context):
        return visitor.visit_call_argument(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("name", name).add("value", value).omitNullValues().toString();
    #     """
