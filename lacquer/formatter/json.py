from collections import OrderedDict
from lacquer.tree import QualifiedName, QuerySpecification
from lacquer.tree.node import Node
from json import JSONEncoder


class NodeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySpecification):
            keys = ("select", "from_", "where", "group_by", "having", "order_by", "limit")
            ret = OrderedDict([(key, getattr(obj, key)) for key in keys if getattr(obj, key)])
            return ret

        if isinstance(obj, Node):
            keys = [key for key in obj.__dict__.keys() if
                    key[0] != '_' and key not in ('line', 'pos')]
            ret = {key: getattr(obj, key) for key in keys if getattr(obj, key)}
            return ret

        if isinstance(obj, QualifiedName):
            return obj.parts

        return JSONEncoder.default(self, obj)
