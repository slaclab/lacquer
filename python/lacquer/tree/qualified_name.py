class QualifiedName(object):
    def __init__(self, parts=None):
        self.parts = parts

    # def of(self, first, rest):
    #     pass
    #
    # def has_suffix(self, suffix):
    #     pass

    def __str__(self):
        return '.'.join(self.parts or [])  # TODO: .lower() ?

    def __repr__(self):
        return "QualifiedName(%s)" % '.'.join(self.parts or [])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.parts == other.parts
        return False
