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


class GroupingElement(Node):
    def __init__(self, line=None, pos=None):
        super(GroupingElement, self).__init__(line, pos)

    # def enumerate_grouping_sets(self):
    #     pass


class GroupingSets(GroupingElement):
    def __init__(self, line=None, pos=None, sets=None):
        super(GroupingSets, self).__init__(line, pos)
        self.sets = sets

    # def enumerate_grouping_sets(self):
    #     pass

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("sets", sets).toString();
    #     """


class SimpleGroupBy(GroupingElement):
    def __init__(self, line=None, pos=None, columns=None):
        super(SimpleGroupBy, self).__init__(line, pos)
        self.columns = columns

    # def enumerate_grouping_sets(self):
    #     pass

    # def __str__(self):
    #     """
    #     return MoreObjects.toStringHelper(this).add("columns", columns).toString();
    #     """
