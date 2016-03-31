

class QualifiedName(object):
    def __init__(self, parts=None, original_parts=None):
        self.parts = parts
        self.original_parts = original_parts

    # def of(self, first, rest):
    #     pass
    #
    # def has_suffix(self, suffix):
    #     pass

    def __str__(self):
        return '.'.join(self.original_parts or [])
