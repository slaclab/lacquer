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

from collections import OrderedDict

from lacquer import parser
from lacquer.tree import AliasedRelation
from lacquer.tree import Join
from lacquer.tree import DefaultTraversalVisitor
from lacquer.tree import QualifiedNameReference
from lacquer.tree import SingleColumn
from lacquer.tree import Table


def check_extracted_columns(query, with_resolution=False):

    class TableAndColumnExtractor(DefaultTraversalVisitor):
        def __init__(self):
            self.columns = []
            self.tables = []

        def visit_query_specification(self, node, context):
            for item in node.select.select_items:
                if isinstance(item, SingleColumn):
                    self.columns.append(item)

            if node.from_:
                self.tables = []
                if isinstance(node.from_, Join):
                    relation = node.from_
                    self.tables.append(relation.right)
                    while isinstance(relation.left, Join):
                        relation = relation.left
                        self.tables.append(relation.right)
                    self.tables.append(relation.left)
                else:
                    self.tables.append(node.from_)
                self.tables.reverse()

    def print_column_resolution_order(columns, tables):
        table_columns = []
        tables_and_aliases = OrderedDict()
        for i in range(len(columns)):
            column = columns[i]
            if isinstance(column.expression, QualifiedNameReference):
                table_columns.append((column, i))

        for table in tables:
            if isinstance(table, AliasedRelation):
                if isinstance(table.relation, Table):
                    tables_and_aliases[table.alias] = table.relation
                else:
                    print("WARNING: Aliased Relation is not a table and is omitted")
            else:
                tables_and_aliases[".".join(table.name.parts)] = table

        print("\nTable Column Resolution:")
        for (column, position) in table_columns:
            names = column.expression.name.parts
            column_name = names[-1]
            resolution = []
            if len(names) > 1:
                qualified_table_name = ".".join(names[:-1])
                if qualified_table_name in tables_and_aliases:
                    resolution.append(tables_and_aliases[qualified_table_name])
            else:
                resolution = [v for v in tables_and_aliases.values()]
            print(repr(column) + ": " + str(resolution))

    print("\n\nChecking query:\n" + query)
    visitor = TableAndColumnExtractor()
    visitor.process(parser.parse(query), None)
    print(visitor.columns)
    print(visitor.tables)
    if with_resolution:
        print_column_resolution_order(visitor.columns, visitor.tables)


def check_has_subquery(query):

    class SubqueryCheck(DefaultTraversalVisitor):
        has_subquery = False

        def visit_subquery_expression(self, node, context):
            self.has_subquery = True

    print("Checking query:\n%s" % query)
    checker = SubqueryCheck()
    checker.process(parser.parse(query))
    has_subquery = "not " if not checker.has_subquery else ""
    print("...query does %shave a subquery.\n" % has_subquery)

if __name__ == "__main__":
    print("Running column extractors\n\n")
    check_extracted_columns("select a, b from c, d")
    check_extracted_columns("select a as foo, b as bar from c, d")
    check_extracted_columns("select foo.a as foo_a, bar.b as bar_b, c from foo, bar", True)
    check_extracted_columns("select foo.a as foo_a, bar.b as bar_b, c from x foo, y bar", True)
    check_extracted_columns("select foo.a as foo_a, bar.b as bar_b, c "
                            "from (select a from foo) foo, y bar", True)
    check_extracted_columns("select a, b from c join d using(foo) join e using (bar)")
    check_extracted_columns("select 1, a from c join d using(foo) join e using (bar)")
    check_extracted_columns("select (select 1 from foo), a "
                            "from c join d using(foo) join e using (bar)")
    check_extracted_columns("select 1, 20+a from c join d using(foo) join e using (bar)")

    print("Running subquery checkers\n\n")
    check_has_subquery("select a from b")
    check_has_subquery("select a from (select a from b)")
    check_has_subquery("select a, (select count(1) from foo) from foo")
