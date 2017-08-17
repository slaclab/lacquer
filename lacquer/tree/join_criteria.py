# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from inspect import getargspec


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
        clz = self.__class__
        argspec = [x for x in getargspec(clz.__init__).args[1:] if self.__dict__[x] is not None]
        args = ", ".join(["=".join((arg, repr(getattr(self, arg)))) for arg in argspec])
        return "{name}({args})".format(name=clz.__name__, args=args)


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
