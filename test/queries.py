import unittest
import os
from lacquer.parsers.parser import parser
from lacquer.formatter.formatter import format_sql
from lacquer.formatter.json import NodeEncoder


class TestQueries(unittest.TestCase):

    def setUp(self):
        test_queries = []
        current_query = []
        with open(os.path.join(os.path.dirname(__file__), "queries.sql")) as queries:
            for line in queries.readlines():
                line = line[:-1]
                if not len(line.strip()):
                    continue
                if line.strip()[-1] == ";":
                    idx = line.rfind(";")
                    current_query.append(line[0:idx])
                    test_queries.append('\n'.join(current_query))
                    current_query = []
                else:
                    current_query.append(line)
        self.queries = test_queries

    def test_parse_queries(self):
        err = 0
        for query in self.queries:
            try:
                tree = parser.parse(query, tracking=True)
            except SyntaxError as e:
                print("Error parsing query:")
                e.print_file_and_line(e)
                err +=1

    def test_format_queries(self):
        err = 0
        for query in self.queries:
            try:
                tree = parser.parse(query, tracking=True)
                try:
                    format_sql(tree)
                except Exception as e:
                    import time
                    import traceback
                    print("\n\n")
                    print(query)
                    print("failed to format:\n" + str(tree))
                    print(e)
                    traceback.print_tb(e.__traceback__)
                    #time.sleep(1)
                    print("\n\n")
            except SyntaxError as e:
                #print("Error parsing query <skipped>")
                err +=1

    def test_format_json(self):
        err = 0
        for query in self.queries:
            try:
                print(query)
                tree = parser.parse(query, tracking=True)
                print(NodeEncoder(indent=4).encode(tree))
            except SyntaxError as e:
                err +=1



if __name__ == '__main__':
    unittest.main()
