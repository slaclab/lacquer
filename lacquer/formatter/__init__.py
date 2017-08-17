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

from .formatter import format_sql

from collections import OrderedDict
from lacquer.tree import QualifiedName, QuerySpecification, JoinCriteria
from lacquer.tree.node import Node
from json import JSONEncoder


class JsonNodeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySpecification):
            keys = ("select", "from_", "where", "group_by", "having", "order_by", "limit")
            ret = OrderedDict([(key, getattr(obj, key)) for key in keys if getattr(obj, key)])
            return ret

        if isinstance(obj, (Node, JoinCriteria)):
            keys = [key for key in obj.__dict__.keys() if
                    key[0] != '_' and key not in ('line', 'pos')]
            ret = {key: getattr(obj, key) for key in keys if getattr(obj, key)}
            return ret

        if isinstance(obj, QualifiedName):
            return obj.parts

        return JSONEncoder.default(self, obj)
