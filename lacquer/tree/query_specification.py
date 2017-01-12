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

from .relation import QueryBody


class QuerySpecification(QueryBody):
    def __init__(self, line=None, pos=None, select=None, from_=None, where=None,
                 group_by=None, having=None, order_by=None, limit=None):
        super(QuerySpecification, self).__init__(line, pos)
        self.select = select
        self.from_ = from_
        self.where = where
        self.group_by = group_by
        self.having = having
        self.order_by = order_by or []
        self.limit = limit

    def accept(self, visitor, context):
        return visitor.visit_query_specification(self, context)

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("select", select).add("from", from).add("where", where.orNull())
    #         .add("groupBy", groupBy).add("having", having.orNull()).add("orderBy", orderBy)
    #         .add("limit", limit.orNull()).toString();
    #     """
