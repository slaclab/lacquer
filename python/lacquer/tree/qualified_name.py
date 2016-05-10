from inspect import getargspec


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
