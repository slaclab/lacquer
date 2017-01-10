import unittest
from collections import OrderedDict

from lacquer.parsers.parser import parser
from lacquer.tree import AliasedRelation
from lacquer.tree import Join
from lacquer.tree import DefaultTraversalVisitor
from lacquer.tree import QualifiedNameReference
from lacquer.tree import SingleColumn
from lacquer.tree import Table


class TestGather(unittest.TestCase):

    def test_gather(self):

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

        def extract(query):
            visitor = TableAndColumnExtractor()
            visitor.process(parser.parse(query), None)
            return visitor.columns, visitor.tables

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

        def check(query, with_resolution=False):
            print("\n\nChecking query:\n" + query)
            columns, tables = extract(query)
            print(columns)
            print(tables)
            if with_resolution:
                print_column_resolution_order(columns, tables)

        check("select a, b from c, d")
        check("select a as foo, b as bar from c, d")
        check("select foo.a as foo_a, bar.b as bar_b, c from foo, bar", True)
        check("select foo.a as foo_a, bar.b as bar_b, c from x foo, y bar", True)
        check("select foo.a as foo_a, bar.b as bar_b, c from (select a from foo) foo, y bar", True)
        check("select a, b from c join d using(foo) join e using (bar)")
        check("select 1, a from c join d using(foo) join e using (bar)")
        check("select (select 1 from foo), a from c join d using(foo) join e using (bar)")
        check("select 1, 20+a from c join d using(foo) join e using (bar)")

    def test_has_subquery(self):

        class SubqueryCheck(DefaultTraversalVisitor):
            has_subquery = False

            def visit_subquery_expression(self, node, context):
                self.has_subquery = True

        checker = SubqueryCheck()
        print(checker.process(parser.parse("select a from b"), None))
        print(checker.has_subquery)

        checker = SubqueryCheck()
        checker.process(parser.parse("select a from (select a from b)"), None)
        print(checker.has_subquery)

        checker = SubqueryCheck()
        checker.process(parser.parse("select a, (select count(1) from foo) from foo"), None)
        print(checker.has_subquery)

