from .node import Node


class Window(Node):
    def __init__(self, line=None, pos=None, partition_by=None, order_by=None, frame=None):
        super(Window, self).__init__(line, pos)
        self.partition_by = partition_by
        self.order_by = order_by
        self.frame = frame

    def accept(self, visitor, context):
        visitor.visit_window(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this)
    #         #.add("partitionBy", partitionBy)
    #         .add("orderBy", orderBy)
    #         .add("frame", frame).toString();
    #     """


class WindowFrame(Node):
    def __init__(self, line=None, pos=None, type=None, start=None, end=None):
        super(WindowFrame, self).__init__(line, pos)
        self.type = type
        self.start = start
        self.end = end

    def accept(self, visitor, context):
        visitor.visit_window_frame(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("type", type).add("start", start).add("end", end).toString();
    #     """


class FrameBound(Node):
    def __init__(self, line=None, pos=None, type=None, value=None):
        super(FrameBound, self).__init__(line, pos)
        self.type = type
        self.value = value

    def accept(self, visitor, context):
        visitor.visit_frame_bound(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("type", type).add("value", value).toString();
    #     """
