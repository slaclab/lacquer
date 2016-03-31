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
t_DECIMAL = r'[-]?({flits})'.format(flits=_flits)

t_LPAREN = '\('
t_RPAREN = '\)'

t_EQ = r'='
t_NE = r'<>|!='
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_COMMA = r','
t_PLUS = r'\+'
t_MINUS = r'-'
t_ASTERISK = r'\*'
t_SLASH = r'/'
t_PERCENT = r'%'

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


#def t_DIGIT_IDENTIFIER(t):
#    r"""[0-9][a-zA-Z0-9_@:][a-zA-Z0-9_@:]"""
#    val = t.value.lower()
#    if val in reserved:
#        t.type = reserved[val]
#    return t


def t_QUOTED_IDENTIFIER(t):
    r'"( ~" | "" )*"'
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_BACKQUOTED_IDENTIFIER(t):
    r'`( [^`] | `` )*`'
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_SIMPLE_COMMENT(t):
    r"""--[^\r\n]*\r?\n?"""
    t.type = "COMMENT"
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lex.lex()


def p_statement(p):
    r"""statement : query"""
    p[0] = p[1]

##         | USE schema=identifier                                            #use
##         | USE catalog=identifier '.' schema=identifier                     #use
##         | EXPLAIN ('(' explain_option (',' explain_option)* ')')? statement  #explain
##         | DESCRIBE qualified_name                                           #showColumns
##         | DESC qualified_name                                               #showColumns
##         | SHOW TABLES ((FROM | IN) qualified_name)? (LIKE pattern=STRING)?  #showTables
##         | SHOW SCHEMAS ((FROM | IN) identifier)?                           #showSchemas
##         | SHOW CATALOGS                                                    #showCatalogs
##         | SHOW COLUMNS (FROM | IN) qualified_name                           #showColumns
##         | SHOW FUNCTIONS                                                   #showFunctions
##         | CALL qualified_name '(' (callArgument (',' callArgument)*)? ')'   #call
##         | CREATE (OR REPLACE)? VIEW qualified_name AS query                 #createView
##         | DROP VIEW (IF EXISTS)? qualified_name                             #dropView
##         | CREATE TABLE qualified_name
##             (WITH tableProperties)? AS query
##             (WITH (NO)? DATA)?                                             #createTableAsSelect
##         | CREATE TABLE (IF NOT EXISTS)? qualified_name
##             '(' tableElement (',' tableElement)* ')'
##             (WITH tableProperties)?                                        #createTable
##         | DROP TABLE (IF EXISTS)? qualified_name                            #dropTable
##         | INSERT INTO qualified_name column_aliases? query                   #insertInto
##         | DELETE FROM qualified_name (WHERE boolean_expression)?             #delete
##         | ALTER TABLE from=qualified_name RENAME TO to=qualified_name        #renameTable
##         | ALTER TABLE tableName=qualified_name
##             RENAME COLUMN from=identifier TO to=identifier                 #renameColumn
##         | ALTER TABLE tableName=qualified_name
##             ADD COLUMN column=tableElement                                 #addColumn
##         | SHOW SESSION                                                     #showSession
##         | SET SESSION qualified_name EQ expression                          #setSession
##         | RESET SESSION qualified_name                                      #resetSession
##         | START TRANSACTION (transactionMode (',' transactionMode)*)?      #startTransaction
##         | COMMIT WORK?                                                     #commit
##         | ROLLBACK WORK?                                                   #rollback
##     """
##     return p


# """table_properties : '(' table_property (',' table_property)* ')'"""
# """table_property : identifier EQ expression"""

# TODO : Check this

def p_query_term(p):
    r"""query_term : query_primary
                   | query_term INTERSECT set_quantifier_opt query_term
                   | query_term UNION     set_quantifier_opt query_term
                   | query_term EXCEPT    set_quantifier_opt query_term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        left = p[1]
        op = p[2]
        distinct = p[3] is None or p[3] == "DISTINCT"
        right = p[4]

        if op == "UNION":
            p[0] = Union(p.lineno(1), p.lexpos(1), relations=[left, right], distinct=distinct)
        elif op == "INTERSECT":
            p[0] = Intersect(p.lineno(1), p.lexpos(1), relations=[left, right], distinct=distinct)
        elif op == "EXCEPT":
            p[0] = Except(p.lineno(1), p.lexpos(1), distinct=distinct)
        else:
            raise ValueError("Unsupported set operation: " + op)


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
    return p[3] if p[1] else None


def p_limit_opt(p):
    r"""limit_opt : LIMIT INTEGER
                  | LIMIT ALL
                  | empty"""
    return p[3] if p[1] else None


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
        for rel in from_relations:
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
    return p[2] if p[1] else None


def p_where_opt(p):
    r"""where_opt : WHERE boolean_expression
                 | empty"""
    return p[2] if p[1] else None


def p_group_by_opt(p):
    r"""group_by_opt : GROUP BY set_quantifier_opt grouping_elements
                     | empty"""
    return p[3] if p[1] else None


def p_having_opt(p):
    r"""having_opt : HAVING boolean_expression
                 | empty"""
    return p[2] if p[1] else None


def p_select_items(p):
    r"""select_items : select_items COMMA select_item
                     | select_item"""
    _item_list(p)


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


# TODO: groupingSet ?
# TODO: Named query ? (unsupported in MySQL)


def p_set_quantifier_opt(p):
    r"""set_quantifier_opt : DISTINCT
                           | ALL
                           | empty"""
    p[0] = p[1] 


def p_select_item(p):
    r"""select_item : expression alias_opt
                    | qualified_name '.' ASTERISK
                    | ASTERISK"""
    if len(p) == 3:
        p[0] = SingleColumn(p.lineno(1), p.lexpos(1), alias=p[2], expression=p[1])
    else:
        p[0] = AllColumns(p.lineno(1), p.lexpos(1), prefix=p[1] if len(p) == 4 else None)


def p_alias_opt(p):
    r"""alias_opt : AS identifier
                  | identifier
                  | empty"""
    if p[1]:
        p[0] = p[1] if len(p) == 2 else p[2]
    else:
        p[0] = None


def p_relations(p):
    r"""relations : relation
                  | relations COMMA relation"""
    _item_list(p)


def p_relation(p):
    r"""relation : join_relation
                 | aliased_relation"""
    p[0] = p[1]


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
    r"""join_criteria : ON boolean_expression
                      | USING LPAREN identifiers RPAREN"""
    if len(p) == 3:
        p[0] = JoinOn(expression=p[2])
    else:
        p[0] = JoinUsing(columns=p[3])


def p_aliased_relation(p):
    r"""aliased_relation : relation_primary correlation_alias_opt"""
    p[0] = AliasedRelation(p.lineno(1), p.lexpos(1), relation=p[1],
                           alias=p[2].alias, column_names=p[2].column_names)


# Notes: 'AS' in as_opt not supported on most databases
# Column list (aka derived column list) not supported by many databases
def p_correlation_alias_opt(p):
    r"""correlation_alias_opt : as_opt identifier column_list_opt"""
    # Note: We are just using Node for this one rather than creating a new class
    p[0] = Node(p.lineno(1), p.lexpos(1), alias=p[2], column_names=p[3])


def p_column_list_opt(p):
    r"""column_list_opt : LPAREN identifiers RPAREN
                        | empty"""
    p[0] = p[2] if p[1] else None


def p_identifiers(p):
    r"""identifiers : identifier
                    | identifiers COMMA identifier"""
    _item_list(p)


def p_relation_primary(p):
    r"""relation_primary : qualified_name
                         | LPAREN query RPAREN
                         | LPAREN relation RPAREN"""
    p[0] = p[1] if len(p) == 2 else p[2]


def p_expressions(p):
    r"""expressions : expression
                    | expressions COMMA expression"""
    _item_list(p)


def p_expression(p):
    r"""expression : boolean_expression"""
    p[0] = p[1]


def p_boolean_expression(p):
    r"""boolean_expression : or_expression
                           | boolean_expression AND or_expression"""
    print "boolean expression"
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="AND", left=p[1], right=p[2])


def p_or_expression(p):
    r"""or_expression : simple_expression
                      | or_expression OR simple_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalBinaryExpression(p.lineno(1), p.lexpos(1), type="OR", left=p[1], right=p[2])


def p_simple_expression(p):
    r"""simple_expression : predicate
                          | NOT boolean_expression
                          | EXISTS LPAREN query RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = NotExpression(p.lineno(1), p.lexpos(1), value=p[2])
    else:
        p[0] = ExistsPredicate(p.lineno(1), p.lexpos(1), subquery=p[3])


def p_predicate(p):
    r"""predicate : value_expression
                  | value_expression comparison_operator value_expression
                  | value_expression not_opt BETWEEN value_expression AND value_expression
                  | value_expression not_opt IN LPAREN expressions RPAREN
                  | value_expression not_opt IN LPAREN query RPAREN
                  | value_expression not_opt LIKE value_expression
                  | value_expression IS not_opt NULL"""
    # TODO: add:    | value_expression not_opt LIKE value_expression ESCAPE value_expression
    # TODO: maybe:  | value_expression IS not_opt DISTINCT FROM value_expression
    if len(p) == 2:
        p[0] = p[1]
    elif p.slice[2].type == "comparison_operator":
        p[0] = ComparisonExpression(p.lineno(1), p.lexpos(1), type=p[1], left=p[1], right=p[2])
    else:
        if p.slice[3].type == "BETWEEN":
            p[0] = BetweenPredicate(p.lineno(1), p.lexpos(1), value=p[1], min=p[4], max=p[6])
        elif p.slice[3].type == "IN":
            value_list = None
            if p.slice[5].type == "expressions":
                value_list = InListExpression(p.lineno(4), p.lexpos(4), values=p[5])
            elif p.slice[5].type == "query":
                value_list = SubqueryExpression(p.lineno(4), p.lexpos(4), query=p[5])
            else:
                SyntaxError("Shouldn't be here!")
            p[0] = InPredicate(p.lineno(1), p.lexpos(1), value=p[1], value_list=value_list)
        elif p.slice[3].type == "LIKE":
            p[0]= LikePredicate(p.lineno(1), p.lexpos(1), value=p[1], pattern=p[4])
        elif p.slice[2].type == "IS":
            if p[4] == "NULL":
                if p[3]:  # Not null
                    p[0] = IsNotNullPredicate(p.lineno(1), p.lexpos(1), value=p[1])
                else:
                    p[0] = IsNullPredicate(p.lineno(1), p.lexpos(1), value=p[1])
        if p[2] and p.slice[2].type == "not_opt":
            p[0] = NotExpression(line=p[0].line, pos=p[0].pos, value=p[0])

def p_value_expression(p):
    r"""value_expression : term
                         | value_expression PLUS term
                         | value_expression MINUS term
                         | value_expression AT timezone_specifier
                         | string_value_expression"""
    if p.slice[1].type in ("term", "string_value_expression"):
        p[0] = p[1]
    elif p.slice[1].type == "value_expression":
        if p.slice[2].type == "AT":
            # TODO: Implement TimeZone?
            raise SyntaxError("TimeZone specifier not supported")
        else:
            p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1), type=p[2], left=p[1], right=p[3])
    else:
        raise SyntaxError("There's a problem with the value_expression rule")


def p_term(p):
    r"""term : factor
             | term ASTERISK factor
             | term SLASH factor
             | term PERCENT factor"""
    if p.slice[1].type == "factor":
        p[0] = p[1]
    else:
        p[0] = ArithmeticBinaryExpression(p.lineno(1), p.lexpos(1), type=p[2], left=p[1], right=p[3])


def p_factor(p):
    r"""factor : plus_or_minus_opt primary_expression"""
    if p[1]:
        p[0] = ArithmeticUnaryExpression(p.lineno(1), p.lexpos(1), value=p[2], sign=p[1])
    else:
        p[0] = p[2]


def p_string_value_expression(p):
    r"""string_value_expression : value_expression CONCAT value_expression"""
    p[0] = FunctionCall(p.lineno(1), p.lexpos(1), name="concat", arguments=[p[1], p[3]])


# TODO : Check Expressions and Kleene Star/One or more behavior


def p_primary_expression(p):
    r"""primary_expression : literal
                           | identifier"""
    p[0] = p[1]
    ##     | POSITION LPAREN value_expression IN value_expression RPAREN                      #position
    ##     | '(' expression (',' expression)+ ')'                                           #rowConstructor
    ##     | ROW LPAREN expressions RPAREN                                       #rowConstructor
    ##     | qualified_name LPAREN ASTERISK RPAREN                                            #functionCall
    ##     | qualified_name LPAREN ( set_quantifier_opt expressions)? RPAREN     #functionCall
    ##     | LPAREN query RPAREN                                                               #subqueryExpression
    ##     | CASE value_expression when_clause+ else_opt END         #simpleCase
    ##     | CASE whenClause+ else_opt END                         #searchedCase
    ##     | CAST RPAREN expression AS type LPAREN                                                #cast
    ##     | TRY_CAST LPAREN expression AS type RPAREN                                            #cast

    ##     | identifier                                                                     #columnReference
    ##     | primary_expression . identifier                                #dereference
    ##     | SUBSTRING LPAREN value_expression FROM value_expression (FOR value_expression)? RPAREN  #substring
    ##     | LPAREN expression RPAREN                                                             #parenthesizedExpression"""
    ##     | CURRENT_DATE                                                              #specialDateTimeFunction
    ##     | CURRENT_TIME    integer_param_opt                           #specialDateTimeFunction
    ##     | CURRENT_TIMESTAMP    integer_param_opt                    #specialDateTimeFunction
    ##     | LOCALTIME    integer_param_opt                             #specialDateTimeFunction
    ##     | LOCALTIMESTAMP    integer_param_opt                         #specialDateTimeFunction

    ###     | identifier '->' expression                                                     #lambda
    ###     | LPAREN identifiers RPAREN '->' expression                           #lambda
    ###     | ARRAY '[' (expressions)? ']'                                  #arrayConstructor
    ###     | primary_expression '[' value_expression ']'                          #subscript
    ###     | NORMALIZE LPAREN value_expression (',' normalForm)? RPAREN                            #normalize
    ###     | EXTRACT LPAREN identifier FROM value_expression RPAREN                                #extract


def p_literal(p):
    r"""literal : NULL
                | number
                | boolean_value
                | STRING
                | interval
                | identifier STRING"""
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
    r"""interval : INTERVAL plus_or_minus_opt STRING interval_field interval_end_opt"""
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


def p_plus_or_minus_opt(p):
    r"""plus_or_minus_opt : PLUS
                          | MINUS
                          | empty"""
    p[0] = p[1]


def p_table_element(p):
    """table_element : IDENTIFIER type"""
    p[0] = TableElement(p.lineno(1), p.lexpos(1), name=p[1], typedef=p[2])


def p_type(p):
    """type : base_type integer_parameter_opt"""
    p[0] = "%s%s" % (p[1], p[2] or '')


def p_integer_parameter_opt(p):
    """integer_parameter_opt : LPAREN INTEGER RPAREN
                             | empty"""
    p[0] = "(%s)" % p[2] if p[1] else None


def p_base_type(p):
    """base_type : IDENTIFIER"""
    p[0] = p[1]


def p_when_clause(p):
    r"""when_clause : WHEN expression THEN expression"""
    p[0] = WhenClause(p.lineno(1), p.lexpos(1), operand=p[2], result=p[4])


    ### explain_option
    ###     : FORMAT value=(TEXT | GRAPHVIZ)         #explainFormat
    ###     | TYPE value=(LOGICAL | DISTRIBUTED)     #explainType
    ### transactionMode
    ###     : ISOLATION LEVEL levelOfIsolation    #isolationLevel
    ###     | READ accessMode=(ONLY | WRITE)      #transactionAccessMode
    ### levelOfIsolation
    ###     : READ UNCOMMITTED                    #readUncommitted
    ###     | READ COMMITTED                      #readCommitted
    ###     | REPEATABLE READ                     #repeatableRead
    ###     | SERIALIZABLE                        #serializable

    ## callArgument
    ##     : expression                    #positionalArgument
    ##     | identifier '=>' expression    #namedArgument

def p_qualified_name(p):
    r"""qualified_name : identifier
                       | qualified_name '.' identifier"""
    return _item_list(p)


def p_identifier(p):
    r"""identifier : IDENTIFIER
                   | quoted_identifier
                   | non_reserved
                   | BACKQUOTED_IDENTIFIER
                   | DIGIT_IDENTIFIER"""
    p[0] = p[1]


def p_non_reserved(p):
    r"""non_reserved : NON_RESERVED"""
    p[0] = p[1]

def p_quoted_identifier(p):
    r"""quoted_identifier : QUOTED_IDENTIFIER"""
    p[0] = p[1]


def p_number(p):
    r"""number : DECIMAL
               | INTEGER"""
    if p.slice[1].type == "DECIMAL":
        p[0] = DoubleLiteral(p.lineno(1), p.lexpos(1), p[1])
    else:
        p[0] = LongLiteral(p.lineno(1), p.lexpos(1), p[1])


#def

    ## STRING
    ##     : '\'' ( ~'\'' | '\'\'' )* '\''
    ##     ;

    ## normalForm
    ##     : NFD | NFC | NFKD | NFKC
    ## // Note: we allow any character inside the binary literal and validate
    ## // its a correct literal when the AST is being constructed. This
    ## // allows us to provide more meaningful error messages to the user
    ## BINARY_LITERAL
    ##     :  'X\'' (~'\'')* '\''
    ##     ;

    ## TIME_WITH_TIME_ZONE
    ##     : 'TIME' WS 'WITH' WS 'TIME' WS 'ZONE'
    ##     ;

    ## TIMESTAMP_WITH_TIME_ZONE
    ##     : 'TIMESTAMP' WS 'WITH' WS 'TIME' WS 'ZONE'
    ##     ;

    ## WS
    ##     : [ \r\n\t]+ -> channel(HIDDEN)
    ##     ;

    ## // Catch-all for anything we can't recognize.
    ## // We use this to be able to ignore and recover all the text
    ## // when splitting statements with DelimiterLexer
    ## UNRECOGNIZED
    ##     : .
    ##     ;


def p_empty(p):
    """empty :"""
    pass


def p_error(p):
    print p
    print "Syntax error in input!"


parser = yacc.yacc()

print repr(parser.parse("SELECT 1 , 2 ", tracking=True))
#print parser.parse("SELECT 1, 2 ", tracking=True, debug=True)
print parser.parse("SELECT 1 FROM dual", tracking=True, debug=True)

