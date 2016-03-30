
class JoinCriteria(object):
    def __init__(self, line=None, pos=None):
        self.line = line
        self.pos = pos

    def __str__(self):
        """
        """
        pass


class JoinUsing(JoinCriteria):
    def __init__(self, line=None, pos=None, columns=None):
        super(JoinUsing, self).__init__(line, pos)
        self.columns = columns

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).addValue(columns).toString();
        """
        pass


class NaturalJoin(JoinCriteria):
    def __init__(self, line=None, pos=None):
        super(NaturalJoin, self).__init__(line, pos)

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).toString();
        """
        pass


class JoinOn(JoinCriteria):
    def __init__(self, line=None, pos=None, expression=None):
        super(JoinOn, self).__init__(line, pos)
        self.expression = expression

    def __str__(self):
        """
        return MoreObjects.toStringHelper(this).addValue(expression).toString();
        """
        pass
