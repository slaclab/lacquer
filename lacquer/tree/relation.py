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

from .node import Node
from lacquer.utils import node_str_omit_none


class Relation(Node):
    def __init__(self, line=None, pos=None):
        super(Relation, self).__init__(line, pos)

    def accept(self, visitor, context):
        return visitor.visit_relation(self, context)


class AliasedRelation(Relation):
    def __init__(self, line=None, pos=None, relation=None, alias=None, column_names=None):
        super(AliasedRelation, self).__init__(line, pos)
        self.relation = relation
        self.alias = alias
        self.column_names = column_names

    def accept(self, visitor, context):
        return visitor.visit_aliased_relation(self, context)

    def __str__(self):
        return node_str_omit_none(self,
                                  ("alias", self.alias),
                                  ("column_names", self.column_names))


class Join(Relation):
    TYPES = "CROSS LEFT RIGHT FULL INNER".split(" ")

    def __init__(self, line=None, pos=None, join_type=None, left=None, right=None, criteria=None):
        super(Join, self).__init__(line, pos)
        self.join_type = join_type
        self.left = left
        self.right = right
        self.criteria = criteria

    def accept(self, visitor, context):
        return visitor.visit_join(self, context)

    def __str__(self):
        return node_str_omit_none(self,
                                  ("join_type", self.join_type),
                                  ("left", self.left),
                                  ("right", self.right),
                                  ("criteria", self.criteria))


class QueryBody(Relation):
    def __init__(self, line=None, pos=None):
        super(QueryBody, self).__init__(line, pos)

    def accept(self, visitor, context):
        return visitor.visit_query_body(self, context)


# class Unnest(Relation):
#     def __init__(self, line=None, pos=None, expressions=None, with_ordinality=None):
#         super(Unnest, self).__init__(line, pos)
#         self.expressions = expressions
#         self.with_ordinality = with_ordinality
#
#     def accept(self, visitor, context):
#         return visitor.visit_unnest(self, context)
#
#     def __str__(self):
#         """
#         String result = "UNNEST(" + Joiner.on(", ").join(expressions) + ")";
#         if (withOrdinality) {
#             result += " WITH ORDINALITY";
#         }
#         return result;
#         """
#         pass
