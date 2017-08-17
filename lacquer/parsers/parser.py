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

from __future__ import print_function
from ply import yacc
import types

from lacquer.tree import *
from lacquer.parsers.lexer import tokens
tokens = tokens


def p_statement(p):
    r"""statement : cursor_specification"""
    p[0] = p[1]


def p_single_expression(p):
    r"""single_expression : expression"""
    p[0] = p[1]


def p_cursor_specification(p):
    r"""cursor_specification : query_expression order_by_opt limit_opt"""
    if isinstance(p[1], QuerySpecification):
        # When we have a simple query specification
        # followed by order by limit, fold the order by and limit
        # clauses into the query specification (analyzer/planner
        # expects this structure to resolve references with respect
        # to columns defined in the query specification)
        query = p[1]
        limit = p[3]

        # Support Alternative TOP syntax
        if hasattr(query, 'limit'):
            limit = query.limit
        p[0] = Query(p.lineno(1), p.lexpos(1), with_=None,
                     query_body=QuerySpecification(
                         query.line,
                         query.pos,
                         query.select,
                         query.from_,
                         query.where,
                         query.group_by,
                         query.having,
                         p[2],
                         limit
                     ))
    else:
        p[0] = Query(p.lineno(1), p.lexpos(1),
                     with_=None, query_body=p[1], order_by=p[2], limit=p[3])


def p_subquery(p):
    r"""subquery : LPAREN query_expression RPAREN"""
    p[0] = SubqueryExpression(p.lineno(1), p.lexpos(1), query=p[2])


def p_query_expression(p):
    r"""query_expression : query_expression_body"""
    p[0] = p[1]


def p_query_expression_body(p):
    r"""query_expression_body : nonjoin_query_expression
                              | joined_table"""
    p[0] = p[1]


# ORDER BY
def p_order_by_opt(p):
    r"""order_by_opt : ORDER BY sort_items
                     | empty"""
    p[0] = p[3] if p[1] else None


def p_sort_items(p):
    r"""sort_items : sort_item
                   | sort_items COMMA sort_item"""
    _item_list(p)


def p_sort_item(p):
    r"""sort_item : value_expression order_opt null_ordering_opt"""
    p[0] = SortItem(p.lineno(1), p.lexpos(1),
                    sort_key=p[1], ordering=p[2] or 'ASC', null_ordering=p[3])


def p_order_opt(p):
    r"""order_opt : ASC
                  | DESC
                  | empty"""
    p[0] = p[1]


def p_null_ordering_opt(p):
    r"""null_ordering_opt : NULLS FIRST
                          | NULLS LAST
                          | empty"""
    p[0] = p[2] if p[1] else None


# LIMIT
def p_limit_opt(p):
    r"""limit_opt : LIMIT INTEGER
                  | LIMIT ALL
                  | empty"""
    p[0] = p[2] if p[1] else None


# non-join query expression
# QUERY TERM
def p_nonjoin_query_expression(p):
    r"""nonjoin_query_expression : nonjoin_query_term
                        | nonjoin_query_expression UNION set_quantifier_opt nonjoin_query_term
                        | nonjoin_query_expression EXCEPT set_quantifier_opt  nonjoin_query_term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        left = p[1]
        distinct = p[3] is None or p[3].upper() == "DISTINCT"
        right = p[4]
        if p.slice[2].type == "UNION":
            p[0] = Union(p.lineno(1), p.lexpos(1), relations=[left, right], distinct=distinct)
        else:
            p[0] = Except(p.lineno(1), p.lexpos(1), left=p[1], right=p[3], distinct=distinct)


# non-join query term
def p_nonjoin_query_term(p):
    r"""nonjoin_query_term : nonjoin_query_primary
                         | nonjoin_query_term INTERSECT set_quantifier_opt nonjoin_query_primary"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        distinct = p[3] is None or p[3].upper() == "DISTINCT"
        p[0] = Intersect(p.lineno(1), p.lexpos(1), relations=[p[1], p[4]], distinct=distinct)


# non-join query primary
def p_nonjoin_query_primary(p):
    r"""nonjoin_query_primary : simple_table
                              | LPAREN nonjoin_query_expression RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = TableSubquery(p.lineno(1), p.lexpos(1), query=p[2])


def p_simple_table(p):
    r"""simple_table : query_spec
                     | explicit_table
                     | table_value_constructor"""
    p[0] = p[1]


def p_explicit_table(p):
    r"""explicit_table : TABLE qualified_name"""
    p[0] = Table(p.lineno(1), p.lexpos(1), name=p[2])


def p_table_value_constructor(p):
    r"""table_value_constructor : VALUES values_list"""
    p[0] = Values(p.lineno(1), p.lexpos(1), rows=p[2])


def p_values_list(p):
    r"""values_list : values_list COMMA expression
                    | expression"""
    _item_list(p)


def _item_list(p):
    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = None


def p_query_spec(p):
    r"""query_spec : SELECT set_quantifier_opt alt_limit_opt select_items table_expression_opt"""
    distinct = p[2].upper() == "DISTINCT" if p[2] else False
    select_items = p[4]
    table_expression_opt = p[5]
    from_relations = table_expression_opt.from_ if table_expression_opt else None
    where = table_expression_opt.where if table_expression_opt else None
    group_by = table_expression_opt.group_by if table_expression_opt else None
    having = table_expression_opt.having if table_expression_opt else None

    # Reduce the implicit join relations
    from_ = None
    if from_relations:
        from_ = from_relations[0]
        for rel in from_relations[1:]:  # Skip first one
            from_ = Join(p.lineno(5), p.lexpos(5), join_type="IMPLICIT", left=from_, right=rel)

    p[0] = QuerySpecification(p.lineno(1), p.lexpos(1),
                              select=Select(p.lineno(1), p.lexpos(1),
                                            distinct=distinct, select_items=select_items),
                              from_=from_,
                              where=where,
                              group_by=group_by,
                              having=having)
    # Alt-limit (TOP) Support
    if p[3]:
        p[0].limit = p[3]


def p_alt_limit_opt(p):
    r"""alt_limit_opt : TOP INTEGER
                     | empty"""
    p[0] = int(p[2]) if p[1] else None


def p_where_opt(p):
    r"""where_opt : WHERE search_condition
                  | WHERE LPAREN search_condition RPAREN
                  | empty"""
    if p.slice[1].type == "WHERE":
        p[0] = p[2] if len(p) == 3 else p[3]
    else:
        p[0] = None


def p_group_by_opt(p):
    r"""group_by_opt : GROUP BY grouping_expressions
                     | empty"""
    p[0] = SimpleGroupBy(p.lineno(1), p.lexpos(1), columns=p[3]) if p[1] else None


def p_grouping_expressions(p):
    r"""grouping_expressions : value_expression
                             | grouping_expressions COMMA value_expression"""
    _item_list(p)


def p_having_opt(p):
    r"""having_opt : HAVING search_condition
                   | empty"""
    p[0] = p[2] if p[1] else None


def p_set_quantifier_opt(p):
    r"""set_quantifier_opt : DISTINCT
                           | ALL
                           | empty"""
    p[0] = p[1]


def p_select_items(p):
    r"""select_items : select_item
                     | select_items COMMA select_item"""
    _item_list(p)


def p_select_item(p):
    r"""select_item : derived_column
                    | all_columns"""
    p[0] = p[1]


def p_derived_column(p):
    r"""derived_column : value_expression alias_opt"""
    p[0] = SingleColumn(p.lineno(1), p.lexpos(1), alias=p[2], expression=p[1])


def p_all_columns(p):
    r"""all_columns : ASTERISK"""
    p[0] = AllColumns(p.lineno(1), p.lexpos(1), prefix=p[1] if len(p) == 4 else None)


def p_table_expression_opt(p):
    r"""table_expression_opt : FROM relations where_opt group_by_opt having_opt
                             | empty"""
    if p[1]:
        p[0] = Node(p.lineno(1), p.lexpos(1), from_=p[2], where=p[3], group_by=p[4], having=p[5])
    else:
        p[0] = p[1]


def p_relations(p):
    r"""relations : relations COMMA table_reference
                  | table_reference"""
    _item_list(p)


# query expression
def p_table_reference(p):
    r"""table_reference : table_primary
                        | joined_table"""
    p[0] = p[1]


# table reference
def p_table_primary(p):
    r"""table_primary : aliased_relation
                      | derived_table"""
    p[0] = p[1]


# joined table
def p_joined_table(p):
    r"""joined_table : cross_join
                     | qualified_join
                     | natural_join"""
    p[0] = p[1]


def p_cross_join(p):
    r"""cross_join : table_reference CROSS JOIN table_primary"""
    p[0] = Join(p.lineno(1), p.lexpos(1), join_type="CROSS",
                left=p[1], right=p[4], criteria=None)


def p_qualified_join(p):
    r"""qualified_join : table_reference join_type JOIN table_reference join_criteria"""
    right = p[4]
    criteria = p[5]
    join_type = p[2] if p[2] in ("LEFT", "RIGHT", "FULL") else "INNER"
    p[0] = Join(p.lineno(1), p.lexpos(1), join_type=join_type,
                left=p[1], right=right, criteria=criteria)


def p_natural_join(p):
    r"""natural_join : table_reference NATURAL join_type JOIN table_primary"""
    right = p[5]
    criteria = NaturalJoin()
    join_type = "INNER"
    p[0] = Join(p.lineno(1), p.lexpos(1), join_type=join_type,
                left=p[1], right=right, criteria=criteria)


def p_join_type(p):
    r"""join_type : INNER
                  | LEFT outer_opt
                  | RIGHT outer_opt
                  | FULL outer_opt
                  | empty"""
    p[0] = p[1]


def p_outer_opt(p):
    r"""outer_opt : OUTER
                  | empty"""
    # Ignore


def p_join_criteria(p):
    r"""join_criteria : ON search_condition
                      | ON LPAREN search_condition RPAREN
                      | USING LPAREN join_columns RPAREN"""
    if p.slice[1].type == "ON":
        p[0] = JoinOn(expression=p[2] if len(p) == 3 else p[3])
    else:
        p[0] = JoinUsing(columns=p[3])


def p_identifiers(p):
    r"""join_columns : identifier
                     | join_columns COMMA identifier"""
    _item_list(p)


# Potentially Aliased table_reference
def p_aliased_relation(p):
    r"""aliased_relation : qualified_name alias_opt"""
    rel = Table(p.lineno(1), p.lexpos(1), name=p[1])
    if p[2]:
        p[0] = AliasedRelation(p.lineno(1), p.lexpos(1),
                               relation=rel, alias=p[2])  # , column_names=column_names)
    else:
        p[0] = rel


# Notes: 'AS' in as_opt not supported on most databases
# Column list (aka derived column list) not supported by many databases
# See: http://savage.net.au/SQL/sql-92.bnf.html#correlation specification
# FIXME: We omit this for now


def p_derived_table(p):
    r"""derived_table : subquery alias_opt"""
    if p[2]:
        p[0] = AliasedRelation(p.lineno(1), p.lexpos(1), relation=p[1], alias=p[2])
    else:
        p[0] = p[1]


def p_alias_opt(p):
    r"""alias_opt : alias
                  | empty"""
    p[0] = p[1]


def p_alias(p):
    r"""alias : as_opt identifier"""
    p[0] = p[2]


def p_expression(p):
    r"""expression : search_condition"""
    p[0] = p[1]


def p_search_condition(p):
    r"""search_condition :  boolean_term
                         | search_condition OR boolean_term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="OR", left=p[1], right=p[3])


def p_boolean_term(p):
    r"""boolean_term : boolean_factor
                     | boolean_term AND boolean_factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="AND", left=p[1], right=p[3])


def p_boolean_factor(p):
    r"""boolean_factor : not_opt boolean_test"""
    if p[1]:
        p[0] = NotExpression(p.lineno(1), p.lexpos(1), value=p[2])
    else:
        p[0] = p[2]


def p_boolean_test(p):
    r"""boolean_test : boolean_primary"""
    # No IS NOT? (TRUE|FALSE)
    p[0] = p[1]


def p_boolean_primary(p):
    r"""boolean_primary : predicate
                        | value_expression"""
    p[0] = p[1]


def p_predicate(p):
    r"""predicate : comparison_predicate
                  | between_predicate
                  | in_predicate
                  | like_predicate
                  | null_predicate
                  | exists_predicate"""
    # TODO: maybe:  | value_expression IS not_opt DISTINCT FROM value_expression
    p[0] = p[1]


def p_comparison_predicate(p):
    r"""comparison_predicate : value_expression comparison_operator value_expression"""
    p[0] = ComparisonExpression(p.lineno(1), p.lexpos(1), type=p[2], left=p[1], right=p[3])


def p_between_predicate(p):
    r"between_predicate : value_expression not_opt BETWEEN value_expression AND value_expression"
    p[0] = BetweenPredicate(p.lineno(1), p.lexpos(1), value=p[1], min=p[4], max=p[6])
    _check_not(p)


# TODO : value_expression should include subquery in this case

def p_in_predicate(p):
    r"""in_predicate : value_expression not_opt IN in_value"""
    p[0] = InPredicate(p.lineno(1), p.lexpos(1), value=p[1], value_list=p[4])
    _check_not(p)


def p_in_value(p):
    r"""in_value : LPAREN in_expressions RPAREN
                 | subquery"""
    if p.slice[1].type == "subquery":
        p[0] = p[1]
    else:
        p[0] = InListExpression(p.lineno(1), p.lexpos(1), values=p[2])


def p_in_expressions(p):
    r"""in_expressions : value_expression
                       | in_expressions COMMA value_expression"""
    _item_list(p)


# TODO: add:    | value_expression not_opt LIKE value_expression_ ESCAPE value_expression
def p_like_predicate(p):
    r"""like_predicate : value_expression not_opt LIKE value_expression"""
    p[0] = LikePredicate(p.lineno(1), p.lexpos(1), value=p[1], pattern=p[4])
    _check_not(p)


def _check_not(p):
    if p[2] and p.slice[2].type == "not_opt":
        p[0] = NotExpression(line=p[0].line, pos=p[0].pos, value=p[0])


def p_null_predicate(p):
    r"""null_predicate : value_expression IS not_opt NULL"""
    if p[3]:  # Not null
        p[0] = IsNotNullPredicate(p.lineno(1), p.lexpos(1), value=p[1])
    else:
        p[0] = IsNullPredicate(p.lineno(1), p.lexpos(1), value=p[1])


def p_exists_predicate(p):
    r"""exists_predicate : EXISTS subquery"""
    p[0] = ExistsPredicate(p.lineno(1), p.lexpos(1), subquery=p[2])


def p_value_expression(p):
    r"""value_expression : numeric_value_expression"""
    p[0] = p[1]


def p_numeric_value_expression(p):
    r"""numeric_value_expression : numeric_value_expression PLUS term
                                 | numeric_value_expression MINUS term
                                 | term"""
    if p.slice[1].type == "numeric_value_expression":
        p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1),
                                          type=p[2], left=p[1], right=p[3])
    else:
        p[0] = p[1]


def p_term(p):
    r"""term : term ASTERISK factor
             | term SLASH factor
             | term PERCENT factor
             | term CONCAT factor
             | factor"""
    if p.slice[1].type == "factor":
        p[0] = p[1]
    else:
        p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1),
                                          type=p[2], left=p[1], right=p[3])


def p_factor(p):
    r"""factor : sign_opt primary_expression"""
    if p[1]:
        p[0] = ArithmeticUnaryExpression(p.lineno(1), p.lexpos(1), value=p[2], sign=p[1])
    else:
        p[0] = p[2]

# Skipping sql99 numeric primary...


def p_primary_expression(p):
    r"""primary_expression : parenthetic_primary_expression
                           | base_primary_expression"""
    p[0] = p[1]


def p_parenthetic_primary_expression(p):
    r"""parenthetic_primary_expression : LPAREN value_expression RPAREN"""
    p[0] = p[2]


# Value Expression Primary in SQL-92 BNF
def p_base_primary_expression(p):
    r"""base_primary_expression : value
                                | qualified_name
                                | subquery
                                | function_call
                                | date_time
                                | case_specification
                                | cast_specification"""
    if p.slice[1].type == "qualified_name":
        p[0] = QualifiedNameReference(p.lineno(1), p.lexpos(1), name=p[1])
    else:
        p[0] = p[1]


def p_value(p):
    r"""value : NULL
              | STRING
              | number
              | boolean_value"""
    if p.slice[1].type == "NULL":
        p[0] = NullLiteral(p.lineno(1), p.lexpos(1))
    elif p.slice[1].type == "STRING":
        p[0] = StringLiteral(p.lineno(1), p.lexpos(1), p[1][1:-1])  # FIXME: trim quotes?
    else:
        p[0] = p[1]


def p_function_call(p):
    r"""function_call : qualified_name LPAREN call_args RPAREN"""
    # FIXME: Distinct and arguments may need to be corrected
    distinct = p[3] is None or (isinstance(p[3], str) and p[3].upper() == "DISTINCT")
    p[0] = FunctionCall(p.lineno(1), p.lexpos(1), name=p[1], distinct=distinct, arguments=p[3])


def p_call_args(p):
    r"""call_args : call_list
                  | empty_call_args"""
    p[0] = p[1]


def p_empty_call_args(p):
    r"""empty_call_args : ASTERISK
                        | empty"""
    p[0] = []


def p_case_specification(p):
    r"""case_specification : simple_case
                           | searched_case"""
    p[0] = p[1]


def p_simple_case(p):
    r"""simple_case : CASE value_expression when_clauses else_opt END"""
    p[0] = SimpleCaseExpression(p.lineno(1), p.lexpos(1),
                                operand=p[2], when_clauses=p[3], default_value=p[4])


def p_searched_case(p):
    r"""searched_case : CASE when_clauses else_opt END"""
    p[0] = SearchedCaseExpression(p.lineno(1), p.lexpos(1), when_clauses=p[2], default_value=p[3])


def p_cast_specification(p):
    r"""cast_specification : CAST LPAREN value_expression AS data_type RPAREN"""
    p[0] = Cast(p.lineno(1), p.lexpos(1), expression=p[3], data_type=p[5], safe=False)


def p_when_clauses(p):
    r"""when_clauses : when_clauses when_clause
                     | when_clause"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = None


def p_when_clause(p):
    r"""when_clause : WHEN search_condition THEN value_expression"""
    p[0] = WhenClause(p.lineno(1), p.lexpos(1), operand=p[2], result=p[4])


def p_else_clause(p):
    r"""else_opt : ELSE value_expression
                 | empty"""
    p[0] = p[2] if p[1] else None


def p_call_list(p):
    r"""call_list : call_list COMMA expression
                  | expression"""
    _item_list(p)


def p_data_type(p):
    r"""data_type : base_data_type type_param_list_opt"""
    signature = p[1]
    if p[2]:
        # Normalize param list
        type_params = [str(_type) for _type in p[2]]
        signature += "(" + ','.join(type_params) + ")"
    p[0] = signature


def p_type_param_list_opt(p):
    r"""type_param_list_opt : LPAREN type_param_list RPAREN
                            | empty"""
    p[0] = p[2] if p[1] else p[1]


def p_type_param_list(p):
    r"""type_param_list : type_param_list COMMA type_parameter
                        | type_parameter"""
    _item_list(p)


def p_type_parameter(p):
    r"""type_parameter : INTEGER
                       | base_data_type"""
    p[0] = p[1]


def p_base_data_type(p):
    r"""base_data_type : identifier"""
    p[0] = p[1]


def p_date_time(p):
    r"""date_time : CURRENT_DATE
                  | CURRENT_TIME      integer_param_opt
                  | CURRENT_TIMESTAMP integer_param_opt
                  | LOCALTIME         integer_param_opt
                  | LOCALTIMESTAMP    integer_param_opt"""
    precision = p[2] if len(p) == 3 else None
    p[0] = CurrentTime(p.lineno(1), p.lexpos(1), type=p[1], precision=precision)


def p_comparison_operator(p):
    r"""comparison_operator : EQ
                            | NE
                            | LT
                            | LE
                            | GT
                            | GE"""
    p[0] = p[1]


def p_as_opt(p):
    r"""as_opt : AS
               | empty"""
    # Ignore
    pass


def p_not_opt(p):
    r"""not_opt : NOT
                | empty"""
    p[0] = p[1]


def p_boolean_value(p):
    r"""boolean_value : TRUE
                      | FALSE"""
    p[0] = BooleanLiteral(p.lineno(1), p.lexpos(1), value=p[1])


def p_sign_opt(p):
    r"""sign_opt : sign
                 | empty"""
    p[0] = p[1]


def p_sign(p):
    r"""sign : PLUS
             | MINUS"""
    p[0] = p[1]


def p_integer_param_opt(p):
    """integer_param_opt : LPAREN INTEGER RPAREN
                         | empty"""
    p[0] = int(p[2]) if p[1] else None


def p_qualified_name(p):
    r"""qualified_name : qualified_name PERIOD identifier
                       | identifier"""
    parts = [p[1]] if len(p) == 2 else p[1].parts + [p[3]]
    p[0] = QualifiedName(parts=parts)


def p_identifier(p):
    r"""identifier : IDENTIFIER
                   | quoted_identifier
                   | non_reserved
                   | DIGIT_IDENTIFIER"""
    p[0] = p[1]


def p_non_reserved(p):
    r"""non_reserved : NON_RESERVED """
    p[0] = p[1]


def p_quoted_identifier(p):
    r"""quoted_identifier : QUOTED_IDENTIFIER
                          | BACKQUOTED_IDENTIFIER"""
    p[0] = p[1][1:-1]  # FIXME : Trim quotes ?


def p_number(p):
    r"""number : DECIMAL
               | INTEGER"""
    if p.slice[1].type == "DECIMAL":
        p[0] = DoubleLiteral(p.lineno(1), p.lexpos(1), p[1])
    else:
        p[0] = LongLiteral(p.lineno(1), p.lexpos(1), p[1])


def p_empty(p):
    """empty :"""
    pass


def p_error(p):
    if p:
        err = SyntaxError()
        err.lineno = p.lineno
        err.text = p.lexer.lexdata
        err.token_value = p.value

        text_lines = err.text.split("\n")
        line_lengths = [len(line)+1 for line in text_lines]
        err_line_offset = sum(line_lengths[:err.lineno-1])

        err.line = text_lines[err.lineno-1]
        err.offset = p.lexpos - err_line_offset
        err.msg = ("Syntax error at position %d (%s)"
                   % (err.offset, str(err.token_value)))
        def _print_error(self):
            pointer = " " * self.offset + "^" * len(self.token_value)
            print(self.line + "\n" + pointer)
        _print_error = types.MethodType(_print_error, err)
        err.print_file_and_line = _print_error

        raise err
    raise SyntaxError("Syntax error in input. Check your statement")

parser = yacc.yacc(tabmodule="parser_table", debugfile="parser.out")
expression_parser = yacc.yacc(tabmodule="expression_parser_table",
                              start="single_expression",
                              debugfile="expression_parser.out")
