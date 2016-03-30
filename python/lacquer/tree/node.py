

class Node(object):
    def __init__(self, line=None, pos=None, **kwargs):
        self.line = line
        self.pos = pos
        if kwargs:
            for attr, value in kwargs.items():
                setattr(self, attr, value)

    def accept(self, visitor, context):
        visitor.visit_node(self, context)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)


#class NodeLocation:
#    def __init__(self, line=None, pos=None, line=None, char_position_in_line=None):
#        self.line = line
#        self.pos = pos
#        self.line = line
#        self.char_position_in_line = charPositionInLine
#
