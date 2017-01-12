class QualifiedName(object):
    def __init__(self, parts=None):
        self.parts = parts

    @staticmethod
    def of(*parts):
        """
        Convenience method for constructiong QualfiedNames.
        :param parts: If len(parts) == 1, will split on the periods for you
        """
        if len(parts) == 1 and "." in parts:
            parts = parts[0].split(".")
        return QualifiedName(parts=[part for part in parts])

    def __str__(self):
        return '.'.join(self.parts or [])  # TODO: .lower() ?

    def __repr__(self):
        return "QualifiedName(%s)" % '.'.join(self.parts or [])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.parts == other.parts
        return False
