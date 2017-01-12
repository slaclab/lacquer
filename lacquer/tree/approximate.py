from .node import Node


class Approximate(Node):
    def __init__(self, line=None, pos=None, confidence=None):
        super(Approximate, self).__init__(line, pos)
        self.confidence = confidence

    def accept(self, visitor, context):
        return visitor.visit_approximate(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("confidence", confidence).toString();
    #     """
