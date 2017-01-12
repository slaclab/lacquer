
class JoinCriteria(object):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # skip dunders
            keys = [key for key in self.__dict__.keys() if "__" not in key]
            for key in keys:
                if getattr(self, key) != getattr(other, key):
                    return False
            return True
        return False

    def __repr__(self):
        return str(self)


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
