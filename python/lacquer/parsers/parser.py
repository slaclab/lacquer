from ply import lex, yacc

from lacquer.reserved import *
from lacquer.tree import *

reserved = sorted(set(presto_tokens).difference(presto_nonreserved))

tokens = ['INTEGER',               'DECIMAL',
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
          'NON_RESERVED',
          ] + reserved + list(presto_nonreserved)

_exponent = r'[eE][+-]?\d+'
_flit1 = r'\d+\.\d*({exp})?'.format(exp=_exponent)
_flit2 = r'\.\d+({exp})?'.format(exp=_exponent)
_flit3 = r'\d+({exp})'.format(exp=_exponent)  # require exponent
_flits = '|'.join([_flit1, _flit2, _flit3])
t_DECIMAL = r'({flits})'.format(flits=_flits)

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
    return t


def t_QUOTED_IDENTIFIER(t):
    r'"( ~" | "" )*"'
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


def p_query_term(p):
    r"""query_term : query_term_except
                   | query_term INTERSECT set_quantifier_opt query_term_except"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        left = p[1]
        distinct = p[3] is None or p[3] == "DISTINCT"
        right = p[4]
        p[0] = Intersect(p.lineno(1), p.lexpos(1), relations=[left, right], distinct=distinct)


def p_query_term_except(p):
    r"""query_term_except : query_term_union
                          | query_term_except EXCEPT set_quantifier_opt query_term_union"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        distinct = p[3] is None or p[3] == "DISTINCT"
        p[0] = Except(p.lineno(1), p.lexpos(1), left=p[1], right=p[3], distinct=distinct)


def p_query_term_union(p):
    r"""query_term_union : query_primary
                         | query_term_union UNION set_quantifier_opt query_primary"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        distinct = p[3] is None or p[3] == "DISTINCT"
        p[0] = Union(p.lineno(1), p.lexpos(1), relations=[p[1], p[3]], distinct=distinct)


def p_query_primary(p):
    r"""query_primary : query_specification
                      | TABLE qualified_name
                      | VALUES expressions
                      | LPAREN query RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1] == "TABLE":
            p[0] = Table(p.lineno(1), p.lexpos(1), name=p[2])
        elif p[1] == "VALUES":
            p[0] = Values(p.lineno(1), p.lexpos(1), rows=p[2])
        elif p[1] == "(":
            p[0] = TableSubquery(p.lineno(1), p.lexpos(1), query=p[2])


def p_query(p):
    r"""query : query_term order_by_opt limit_opt"""
    term = p[1]
    if isinstance(term, QuerySpecification):
        # When we have a simple query specification
        # followed by order by limit, fold the order by and limit
        # clauses into the query specification (analyzer/planner
        # expects this structure to resolve references with respect
        # to columns defined in the query specification)
        query = term
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
                         p[3]
                     ))
    else:
        p[0] = Query(p.lineno(1), p.lexpos(1),
                     with_=None, query_body=term, order_by=p[2], limit=p[3])


def p_order_by_opt(p):
    r"""order_by_opt : ORDER BY sort_items
                     | empty"""
    p[0] =  p[3] if p[1] else None


def p_limit_opt(p):
    r"""limit_opt : LIMIT INTEGER
                  | LIMIT ALL
                  | empty"""
    p[0] = p[3] if p[1] else None


def _item_list(p):
    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = None


def p_sort_items(p):
    r"""sort_items : sort_item
                   | sort_items COMMA sort_item"""
    _item_list(p)


def p_sort_item(p):
    r"""sort_item : expression order_opt null_ordering_opt"""
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


def p_query_specification(p):
    r"""query_specification : SELECT set_quantifier_opt select_items from_opt where_opt group_by_opt having_opt"""
    distinct = p[2] == "DISTINCT"
    select_items = p[3]
    from_relations = p[4]
    where = p[5]
    group_by = p[6]
    having = p[7]

    # Reduce the implicit join relations
    from_ = None
    if from_relations:
        from_ = from_relations[0]
        for rel in from_relations[1:]: # Skip first one
            from_ = Join(p.lineno(4), p.lexpos(4), join_type="IMPLICIT", left=from_, right=rel)

    p[0] = QuerySpecification(p.lineno(1), p.lexpos(1),
                              select=Select(p.lineno(1), p.lexpos(1),
                                            distinct=distinct, select_items=select_items),
                              from_=from_,
                              where=where,
                              group_by=group_by,
                              having=having)


def p_from_opt(p):
    r"""from_opt : FROM relations
                 | empty"""
    p[0] = p[2] if p[1] else None


def p_relations(p):
    r"""relations : relations COMMA relation
                  | relation"""
    _item_list(p)


def p_relation(p):
    r"""relation : join_relation
                 | aliased_relation"""
    p[0] = p[1]


def p_where_opt(p):
    r"""where_opt : WHERE expression
                  | empty"""
    p[0] = p[2] if p[1] else None


def p_group_by_opt(p):
    r"""group_by_opt : GROUP BY set_quantifier_opt grouping_elements
                     | empty"""
    p[0] = p[3] if p[1] else None


def p_having_opt(p):
    r"""having_opt : HAVING expression
                   | empty"""
    p[0] = p[2] if p[1] else None


def p_grouping_elements(p):
    r"""grouping_elements : grouping_element
                          | grouping_elements COMMA grouping_element"""
    _item_list(p)


def p_grouping_element(p):
    r"""grouping_element : grouping_expressions"""
    p[0] = p[1]


def p_grouping_expressions(p):
    r"""grouping_expressions : expression
                             | LPAREN expressions RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


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


def p_alias_opt(p):
    r"""alias_opt : as_opt identifier
                  | empty"""
    p[0] = p[2] if len(p) == 3 else p[1]


def p_join_relation(p):
    r"""join_relation : relation CROSS JOIN aliased_relation
                      | relation join_type JOIN relation join_criteria
                      | relation NATURAL join_type JOIN aliased_relation"""
    if p[2] == "CROSS":
        p[0] = Join(p.lineno(1), p.lexpos(1), join_type="CROSS",
                    left=p[1], right=p[3], criteria=None)
    else:
        if p[2] == "NATURAL":
            right = p[5]
            criteria = NaturalJoin()
        else:
            right = p[4]
            criteria = p[5]
        join_type = p[2] if p[2] in ("LEFT", "RIGHT", "FULL") else "INNER"
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
    pass


def p_join_criteria(p):
    r"""join_criteria : ON expression
                      | USING LPAREN join_columns RPAREN"""
    if len(p) == 3:
        p[0] = JoinOn(expression=p[2])
    else:
        p[0] = JoinUsing(columns=p[3])


def p_identifiers(p):
    r"""join_columns : identifier
                     | join_columns COMMA identifier"""
    _item_list(p)


def p_aliased_relation(p):
    r"""aliased_relation : relation_primary correlation_alias_opt"""
    if p[2]:
        alias = p[2].alias
        column_names = p[2].column_names
        p[0] = AliasedRelation(p.lineno(1), p.lexpos(1),
                               relation=p[1], alias=alias, column_names=column_names)
    else:
        p[0] = p[1]


# Notes: 'AS' in as_opt not supported on most databases
# Column list (aka derived column list) not supported by many databases
def p_correlation_alias_opt(p):
    r"""correlation_alias_opt : as_opt identifier
                              | empty"""
    # Note: We are just using Node for this one rather than creating a new class
    p[0] = Node(p.lineno(1), p.lexpos(1), alias=p[2]) if p[1] else None


def p_relation_primary(p):
    r"""relation_primary : qualified_name
                         | LPAREN nested_relation RPAREN"""
    p[0] = p[1] if len(p) == 2 else p[2]


def p_nested_relation(p):
    r"""nested_relation : query
                        | relation"""
    p[0] = p[1]


def p_expressions(p):
    r"""expressions : expressions COMMA expression
                    | expression
                    """
    _item_list(p)


def p_expression(p):
    r"""expression : boolean_expression"""
    p[0] = p[1]


def p_boolean_expression(p):
    r"""boolean_expression : boolean_expression AND or_expression
                           | or_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="AND", left=p[1], right=p[2])


def p_or_expression(p):
    r"""or_expression : or_expression OR simple_expression
                      | simple_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="OR", left=p[1], right=p[2])


def p_simple_expression(p):
    r"""simple_expression : boolean_factor"""
    p[0] = p[1]


def p_boolean_factor(p):
    r"""boolean_factor : not_opt boolean_test"""
    if p[1]:
        p[0] = NotExpression(p.lineno(1), p.lexpos(1), value=p[2])
    else:
        p[0] = p[2]


def p_boolean_test(p):
    r"""boolean_test : boolean_primary"""
    p[0] = p[1]


def p_boolean_primary(p):
    r"""boolean_primary : predicate
                        | LPAREN expression RPAREN"""
    p[0] = p[1] if len(p) == 2 else p[2]


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


def p_in_predicate(p):
    r"""in_predicate : value_expression not_opt IN LPAREN in_value RPAREN"""
    p[0] = InPredicate(p.lineno(1), p.lexpos(1), value=p[1], value_list=p[5])
    _check_not(p)


def p_in_value(p):
    r"""in_value : expressions
                 | query"""
    if p.slice[1].type == "expressions":
        p[0] = InListExpression(p.lineno(1), p.lexpos(1), values=p[1])
    else:
        p[0] = SubqueryExpression(p.lineno(1), p.lexpos(1), query=p[1])


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
    r"""exists_predicate : EXISTS LPAREN query RPAREN"""
    p[0] = ExistsPredicate(p.lineno(1), p.lexpos(1), subquery=p[3])


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


def p_primary_expression(p):
    r"""primary_expression : NULL
                           | number
                           | boolean_value
                           | STRING
                           | interval
                           | identifier STRING
                           | identifier"""
    if p.slice[1].type == "NULL":
        p[0] = NullLiteral(p.lineno(1), p.lexpos(1))
    elif p.slice[1].type == "STRING":
        p[0] = StringLiteral(p.lineno(1), p.lexpos(1), p[1])
    else:
        p[0] = p[1]

    ##     | qualified_name LPAREN ASTERISK RPAREN                                            #functionCall
    ##     | qualified_name LPAREN ( set_quantifier_opt expressions)? RPAREN     #functionCall
    ##     | LPAREN query RPAREN                                                               #subqueryExpression
    ##     | CASE value_expression when_clause+ else_opt END         #simpleCase
    ##     | CASE whenClause+ else_opt END                         #searchedCase
    ##     | CAST RPAREN expression AS type LPAREN                                                #cast

    ##     | '(' expression (',' expression)+ ')'                                           #rowConstructor
    ##     | ROW LPAREN expressions RPAREN                                       #rowConstructor
    ##     | identifier                                                                     #columnReference
    ##     | primary_expression . identifier                                #dereference
    ##     | SUBSTRING LPAREN value_expression FROM value_expression (FOR value_expression)? RPAREN  #substring
    ##     | LPAREN expression RPAREN                                                             #parenthesizedExpression"""
    ##     | CURRENT_DATE                                                              #specialDateTimeFunction
    ##     | CURRENT_TIME    integer_param_opt                           #specialDateTimeFunction
    ##     | CURRENT_TIMESTAMP    integer_param_opt                    #specialDateTimeFunction
    ##     | LOCALTIME    integer_param_opt                             #specialDateTimeFunction
    ##     | LOCALTIMESTAMP    integer_param_opt                         #specialDateTimeFunction


def p_general_literal(p):
    r"""general_literal : STRING
                        | interval"""
    if p.slice[1].type == "NULL":
        p[0] = NullLiteral(p.lineno(1), p.lexpos(1))
    elif p.slice[1].type == "STRING":
        p[0] = StringLiteral(p.lineno(1), p.lexpos(1), p[1].value)
    else:
        p[0] = p[1]


def p_timezone_specifier(p):
    r"""timezone_specifier : TIME ZONE interval
                           | TIME ZONE STRING"""


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
    # Ignore
    p[0] = p[1]


def p_boolean_value(p):
    r"""boolean_value : TRUE
                      | FALSE"""
    p[0] = BooleanLiteral(p.lineno(1), p.lexpos(1), value=p[1])


def p_interval(p):
    r"""interval : INTERVAL sign_opt STRING interval_field interval_end_opt"""
    sign = p[2] or "+"
    p[0] = IntervalLiteral(p.lineno(1), p.lexpos(1), value=p[3], sign=p[2], start_field=p[4], end_field=p[5])


def p_interval_end_opt(p):
    r"""interval_end_opt : TO interval_field
                         | empty"""
    p[0] = p[2] if p[1] else None


def p_interval_field(p):
    r"""interval_field : YEAR
                       | MONTH
                       | DAY
                       | HOUR
                       | MINUTE
                       | SECOND"""
    p[0] = p[1]


def p_sign_opt(p):
    r"""sign_opt : sign
                 | empty"""
    p[0] = p[1]


def p_sign(p):
    r"""sign : PLUS
             | MINUS"""
    p[0] = p[1]

# def p_table_element(p):
#     """table_element : IDENTIFIER type"""
#     p[0] = TableElement(p.lineno(1), p.lexpos(1), name=p[1], typedef=p[2])


# def p_type(p):
#     """type : base_type integer_parameter_opt"""
#     p[0] = "%s%s" % (p[1], p[2] or '')


def p_integer_parameter_opt(p):
    """integer_parameter_opt : LPAREN INTEGER RPAREN
                             | empty"""
    p[0] = "(%s)" % p[2] if p[1] else None


# def p_base_type(p):
#     """base_type : IDENTIFIER"""
#     p[0] = p[1]


def p_when_clause(p):
    r"""when_clause : WHEN expression THEN expression"""
    p[0] = WhenClause(p.lineno(1), p.lexpos(1), operand=p[2], result=p[4])


def p_qualified_name(p):
    r"""qualified_name : qualified_name PERIOD IDENTIFIER
                       | IDENTIFIER"""
    if len(p) == 2:
        parts = [p[1]]
    elif isinstance(p[1], QualifiedName):
        parts = p[1].parts
        parts =[p[3]] + parts
    p[0] = QualifiedName(parts=parts)


def p_identifier(p):
    r"""identifier : IDENTIFIER"""
#                    | quoted_identifier"""
#                   | non_reserved
#                   | DIGIT_IDENTIFIER"""
    p[0] = p[1]


def p_non_reserved(p):
    r"""non_reserved : NON_RESERVED"""
    p[0] = p[1]


def p_quoted_identifier(p):
    r"""quoted_identifier : QUOTED_IDENTIFIER
                          | BACKQUOTED_IDENTIFIER"""
    p[0] = p[1]


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
    print "Syntax error in input!"


parser = yacc.yacc()


print repr(parser.parse("SELECT 1 FROM DUAL", tracking=True))
print repr(parser.parse("SELECT 1 FROM DUAL WHERE 1=1", tracking=True, debug=True))
#print repr(parser.parse("SELECT (SELECT 2 FROM X)", tracking=True, debug=True))
#print repr(parser.parse("(SELECT 1)", tracking=True))
#print repr(parser.parse("SELECT 1, 2", tracking=True))
#print repr(parser.parse("SELECT true", tracking=True))
#print repr(parser.parse("SELECT null", tracking=True))
#print repr(parser.parse("SELECT hi", tracking=True, debug=True))
#print repr(parser.parse("SELECT 'hi'", tracking=True))
#print repr(parser.parse("SELECT `hi`", tracking=True))
#print parser.parse("SELECT 1, 2 ", tracking=True, debug=True)
#print parser.parse("SELECT 1 FROM dual.dual.dual", tracking=True)
#print parser.parse("SELECT 1 FROM dual", tracking=True)

