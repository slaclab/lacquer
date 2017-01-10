from __future__ import print_function
from ply import lex, yacc

from lacquer.reserved import *
from lacquer.tree import *

reserved = sorted(set(presto_tokens).difference(presto_nonreserved))

tokens = ['INTEGER',               'DECIMAL', 'NUMBER',
          'IDENTIFIER',            'DIGIT_IDENTIFIER',
          'QUOTED_IDENTIFIER',     'BACKQUOTED_IDENTIFIER',
          'STRING',                'PERIOD',
          'COMMA',                 'SEMI',
          'PLUS',                  'MINUS',
          'TIMES',                 'DIVIDE',
          'LPAREN',                'RPAREN',
          'GT',                    'GE',
          'LT',                    'LE',
          'EQ',                    'NE',
          'CONCAT',                'SLASH',
          'ASTERISK',              'PERCENT',
          'TOP',  # ADQL
          'NON_RESERVED',
          'COMMENT',
          ] + reserved + list(presto_nonreserved)

# _exponent = r'[eE][+-]?\d+'
# _flit1 = r'\d+\.\d*({exp})?'.format(exp=_exponent)
# _flit2 = r'\.\d+({exp})?'.format(exp=_exponent)
# _flit3 = r'\d+({exp})'.format(exp=_exponent)  # require exponent
# _flits = '|'.join([_flit1, _flit2, _flit3])


def t_NUMBER(t):
    r'\d+(?:\.\d*)?(?:[eE][+-]\d+)?'
    if 'e' in t.value or 'E' in t.value or '.' in t.value:
        t.type = 'DECIMAL'
    else:
        t.type = 'INTEGER'
    return t

t_LPAREN = '\('
t_RPAREN = '\)'

t_EQ = r'='
t_NE = r'<>|!='
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_PERIOD = r'\.'
t_COMMA = r','
t_PLUS = r'\+'
t_MINUS = r'-'
t_ASTERISK = r'\*'
t_SLASH = r'/'
t_PERCENT = r'%'

t_STRING = r"'([^']|'')*'"
t_CONCAT = r'\|\|'

t_ignore = ' \t'


def t_INTEGER(t):
    r'[-]?\d+'
    t.type = "INTEGER"
    return t


def t_IDENTIFIER(t):
    r"""[a-zA-Z_][a-zA-Z0-9_@:]*"""
    val = t.value.lower()
    if val.upper() in reserved:
        t.type = val.upper()
    if val in presto_nonreserved:
        t.type = "NON_RESERVED"
    if val.upper() == "TOP":
        t.type = "TOP"
    return t


def t_QUOTED_IDENTIFIER(t):
    r'"([^"]|"")*"'
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_BACKQUOTED_IDENTIFIER(t):
    r'`([^`]|``)*`'
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_SIMPLE_COMMENT(t):
    r"""--[^\r\n]*\r?\n?"""
    t.type = "COMMENT"
    return t


def t_newline(t):
    r'[\r\n]+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lex.lex()


def p_statement(p):
    r"""statement : query"""
    p[0] = p[1]


def p_subquery(p):
    r"""subquery : LPAREN query RPAREN"""
    p[0] = SubqueryExpression(p.lineno(1), p.lexpos(1), query=p[2])


def p_query(p):
    r"""query : query_no_with"""
    p[0] = p[1]


# FIXME: query expression body or non-join query primary?
def p_query_no_with(p):
    r"""query_no_with : query_term order_by_opt limit_opt"""
    if isinstance(p[1], QuerySpecification):
        # When we have a simple query specification
        # followed by order by limit, fold the order by and limit
        # clauses into the query specification (analyzer/planner
        # expects this structure to resolve references with respect
        # to columns defined in the query specification)
        query = p[1]
        limit = p[3]

        # Support ADQL TOP
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
def p_query_term(p):
    r"""query_term : query_term_intersect
                   | query_term UNION set_quantifier_opt query_term_intersect
                   | query_term EXCEPT set_quantifier_opt query_term_intersect"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        left = p[1]
        distinct = p[3] is None or p[3] == "DISTINCT"
        right = p[4]
        if p[2] == "UNION":
            p[0] = Union(p.lineno(1), p.lexpos(1), relations=[left, right], distinct=distinct)
        else:
            p[0] = Except(p.lineno(1), p.lexpos(1), left=p[1], right=p[3], distinct=distinct)


# non-join query term
def p_query_term_intersect(p):
    r"""query_term_intersect : nonjoin_query_primary
                             | query_term_intersect INTERSECT set_quantifier_opt nonjoin_query_primary"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        distinct = p[3] is None or p[3] == "DISTINCT"
        p[0] = Intersect(p.lineno(1), p.lexpos(1), relations=[p[1], p[3]], distinct=distinct)


# non-join query primary
def p_nonjoin_query_primary(p):
    r"""nonjoin_query_primary : simple_table
                              | LPAREN query_term RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = TableSubquery(p.lineno(1), p.lexpos(1), query=p[2])


def p_simple_table(p):
    r"""simple_table : query_specification
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


def p_query_specification(p):
    r"""query_specification : SELECT set_quantifier_opt adql_top_opt select_items table_expression_opt"""
    distinct = p[2] == "DISTINCT"
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
    # ADQL TOP Support
    if p[3]:
        p[0].limit = p[3]


def p_adql_top_opt(p):
    r"""adql_top_opt : TOP INTEGER
                     | empty"""
    p[0] = int(p[2]) if p[1] else None


def p_where_opt(p):
    r"""where_opt : WHERE search_condition
                  | empty"""
    p[0] = p[2] if p[1] else None


def p_group_by_opt(p):
    r"""group_by_opt : GROUP BY grouping_elements
                     | empty"""
    p[0] = p[3] if p[1] else None


def p_grouping_elements(p):
    r"""grouping_elements : qualified_name
                          | grouping_elements COMMA qualified_name"""
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
                      | derived_table
                      | LPAREN joined_table RPAREN"""
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
                      | USING LPAREN join_columns RPAREN"""
    if len(p) == 3:
        p[0] = JoinOn(expression=p[2])
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
    if p[1] == "not_opt":
        p[0] = NotExpression(p.lineno(1), p.lexpos(1), value=p[2])
    else:
        p[0] = p[2]


def p_boolean_test(p):
    r"""boolean_test : boolean_primary"""
    # No IS NOT? (TRUE|FALSE)
    p[0] = p[1]


def p_boolean_primary(p):
    r"""boolean_primary : predicate
                        | parenthetic_expression"""
    p[0] = p[1] if len(p) == 2 else p[2]


def p_parenthetic_expression(p):
    r"""parenthetic_expression : RPAREN expression RPAREN"""
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
    r"""between_predicate : value_expression not_opt BETWEEN value_expression AND value_expression"""
    p[0] = BetweenPredicate(p.lineno(1), p.lexpos(1), value=p[1], min=p[4], max=p[6])
    _check_not(p)


# TODO : value_expression should include subquery in this case

def p_in_predicate(p):
    r"""in_predicate : value_expression not_opt IN in_value"""
    p[0] = InPredicate(p.lineno(1), p.lexpos(1), value=p[1], value_list=p[4])
    _check_not(p)


def p_in_value(p):
    r"""in_value : LPAREN in_expressions RPAREN"""
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
    r"""value_expression : value_expression PLUS term
                         | value_expression MINUS term
                         | term"""
    if p.slice[1].type in ("term", "string_value_expression"):
        p[0] = p[1]
    elif p.slice[1].type == "value_expression":
        p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1), type=p[2], left=p[1], right=p[3])
    else:
        raise SyntaxError("There's a problem with the value_expression rule")


def p_term(p):
    r"""term : term ASTERISK factor
             | term SLASH factor
             | term PERCENT factor
             | term CONCAT factor
             | factor"""
    if p.slice[1].type == "factor":
        p[0] = p[1]
    else:
        p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1), type=p[2], left=p[1], right=p[3])


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
    r"""parenthetic_primary_expression : LPAREN base_primary_expression RPAREN"""
    p[0] = p[2]


# Value Expression Primary in SQL-92 BNF
def p_base_primary_expression(p):
    r"""base_primary_expression : NULL
                                | number
                                | boolean_value
                                | STRING
                                | qualified_name
                                | function_call
                                | date_time
                                | case_specification
                                | subquery"""
    if p.slice[1].type == "NULL":
        p[0] = NullLiteral(p.lineno(1), p.lexpos(1))
    elif p.slice[1].type == "STRING":
        p[0] = StringLiteral(p.lineno(1), p.lexpos(1), p[1][1:-1])  # FIXME: trim quotes?
    elif p.slice[1].type == "qualified_name":
        p[0] = QualifiedNameReference(p.lineno(1), p.lexpos(1), name=p[1])
    else:
        p[0] = p[1]


def p_function_call(p):
    r"""function_call : qualified_name LPAREN call_list RPAREN"""
    distinct = p[3] is None or p[3] == "DISTINCT"
    p[0] = FunctionCall(p.lineno(1), p.lexpos(1), name=p[1], distinct=distinct, arguments=p[3])


def p_case_specification(p):
    r"""case_specification : simple_case
                           | searched_case"""
    p[0] = p[1]


def p_simple_case(p):
    r"""simple_case : CASE value_expression when_clauses else_opt END"""
    p[0] = SimpleCaseExpression(p.lineno(1), p.lexpos(1), operand=p[2], when_clauses=p[3], default_value=p[4])


def p_searched_case(p):
    r"""searched_case : CASE when_clauses else_opt END"""
    p[0] = SearchedCaseExpression(p.lineno(1), p.lexpos(1), when_clauses=p[2], default_value=p[3])


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
    r"""call_list : call_list COMMA value_expression
                  | value_expression"""
    _item_list(p)


def p_date_time(p):
    r"""date_time : CURRENT_DATE
                  | CURRENT_TIME      integer_param_opt
                  | CURRENT_TIMESTAMP integer_param_opt
                  | LOCALTIME         integer_param_opt
                  | LOCALTIMESTAMP    integer_param_opt"""
    precision = p[2] if len(p) == 3 else None
    p[0] = CurrentTime(p.lineno(1), p.lexpos(1), type=p[1], precision=p[2])


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


def p_table_element(p):
    """table_element : IDENTIFIER type"""
    p[0] = TableElement(p.lineno(1), p.lexpos(1), name=p[1], typedef=p[2])


def p_type(p):
    """type : base_type integer_param_opt"""
    p[0] = "%s%s" % (p[1], ("(%d)" % p[2]) if p[2] else '')


def p_integer_param_opt(p):
    """integer_param_opt : LPAREN INTEGER RPAREN
                         | empty"""
    p[0] = newint(p[2]) if p[1] else None


def p_base_type(p):
    """base_type : IDENTIFIER"""
    p[0] = p[1]


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
        err.msg = "Syntax error"

        discarded_lines = '\n'.join(err.text.split("\n")[:err.lineno-1]) if (err.lineno - 1) else ""
        err.offset = p.lexpos - len(discarded_lines)

        def _print_error(self):
            pointer = " " * err.offset + "^"
            text = '\n'.join(err.text.split("\n")[:err.lineno])
            print(text + "\n" + pointer)
            return text + "\n" + pointer

        err.print_file_and_line = _print_error
        raise err
    raise SyntaxError("Syntax error in input!")

parser = yacc.yacc()
