from inspect import getargspec


class Node(object):
    def __init__(self, line=None, pos=None, **kwargs):
        self.line = line
        self.pos = pos
        if kwargs:
            for attr, value in kwargs.items():
                setattr(self, attr, value)

    def accept(self, visitor, context):
        return visitor.visit_node(self, context)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if v is not None})

    def __repr__(self):
        clz = self.__class__
        argspec = [x for x in getargspec(clz.__init__).args[3:] if self.__dict__[x] is not None]
        args = ", ".join(["=".join((arg, repr(getattr(self, arg)))) for arg in argspec])
        return "{name}({args})".format(name=clz.__name__, args=args)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            keys = [key for key in self.__dict__.keys() if key not in ("line", "pos")]
            for key in keys:
                if getattr(self, key) != getattr(other, key):
                    return False
            return True
        return False

# class NodeLocation:
#    def __init__(self, line=None, pos=None, line=None, char_position_in_line=None):
#        self.line = line
#        self.pos = pos
#        self.line = line
#        self.char_position_in_line = charPositionInLine
#
