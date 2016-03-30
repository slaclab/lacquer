
class JoinCriteria(object):
    pass


class NaturalJoin(JoinCriteria):
    pass


class JoinUsing(JoinCriteria):
    def __init__(self, columns=None):
        self.columns = columns

    def __str__(self):
        return "{}{{columns={}}}".format(self.__class__.__name__, str(self.columns))


class JoinOn(JoinCriteria):
    def __init__(self, expression=None):
        self.expression = expression

    def __str__(self):
        return "{}{{expression={}}}".format(self.__class__.__name__, str(self.expression))
