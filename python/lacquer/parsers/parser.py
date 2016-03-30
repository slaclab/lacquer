from ply import lex, yacc

from lacquer.reserved import *
from lacquer.tree import *

reserved = sorted(set(presto_tokens).difference(presto_nonreserved))

tokens = ['INTEGER',               'DECIMAL',
          'IDENTIFIER',            'DIGIT_IDENTIFIER',
          'QUOTED_IDENTIFIER',     'BACKQUOTED_IDENTIFIER',
          'STRING',
          'COMMA',                 'SEMI',
          'PLUS',                  'MINUS',
          'TIMES',                 'DIVIDE',
          'LPAREN',                'RPAREN',
          'GT',                    'GE',
          'LT',                    'LE',
          'EQ',                    'NE',
          ] + reserved + list(presto_nonreserved)

_exponent = r'[eE][+-]?\d+'
_flit1 = r'\d+\.\d*({exp})?'.format(exp=_exponent)
_flit2 = r'\.\d+({exp})?'.format(exp=_exponent)
_flit3 = r'\d+({exp})'.format(exp=_exponent) # require exponent
_flits = '|'.join([_flit1, _flit2, _flit3])
t_INTEGER = r'[-]?\d+'
t_DECIMAL = r'[-]?({flits})'.format(flits=_flits)

t_LPAREN = '\('
t_RPAREN = '\)'

t_ignore = ' \t'


def t_IDENTIFIER(t):
    r"""[a-zA-Z_][a-zA-Z0-9_@:]*"""
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
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


## def p_statement(p):
##     """statement
##         : query                                                            #statementDefault
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


def p_query_term(p):
    r"""query_term
         : query_primary
         | query_term INTERSECT set_quantifier_opt query_term
         | query_term (UNION | EXCEPT) set_quantifier_opt query_term""" # TODO : Check this
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
    r"""query_primary
            : query_specification
            | TABLE qualified_name                  #table
            | VALUES expressions      #inlineTable
            | LPAREN query RPAREN                 #subquery"""
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
    r"""query:
             query_term
             order_by_opt
             limit_opt"""
    term = p[1]
    if isinstance(term, QuerySpecification):
        # When we have a simple query specification
        # followed by order by limit, fold the order by and limit
        # clauses into the query specification (analyzer/planner
        # expects this structure to resolve references with respect
        # to columns defined in the query specification)
        query = QuerySpecification()
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
        p[0] = Query(p.lineno(1), p.lexpos(1), with_=None, query_body=term, order_by=p[2], limit=p[3])


def p_order_by_opt(p):
    r"""order_by_opt: ORDER BY sort_items | empty"""
    return p[3] if p[1] else None


def p_limit_opt(p):
    r"""limit_opt: LIMIT INTEGER_VALUE | LIMIT ALL | empty"""
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
    r"""sort_items : sort_item | sort_items COMMA sort_item"""
    _item_list(p)


def p_sort_item(p):
    r"""sort_item : expression order_opt null_ordering_opt"""
    p[0] = SortItem(line=None, pos=None, sort_key=p[1], ordering=p[2] or 'ASC', null_ordering=p[3])


def p_order_opt(p):
    r"""order_opt : ASC | DESC | empty"""
    p[0] = p[1]


def p_null_ordering_opt(p):
    r"""null_ordering_opt : NULLS FIRST | NULLS LAST | empty"""
    p[0] = p[2] if p[1] else None


def p_query_specification(p):
    r"""query_specification
            : SELECT set_quantifier_opt select_items
                from_opt
                where_opt
                group_by_opt
                having_opt"""

              #(FROM relations)?
              #(WHERE boolean_expression)?
              #(GROUP BY grouping_elements)?
              #(HAVING boolean_expression)?

def p_from_opt(p):
    r"""from_opt : FROM relations | empty"""
    return p[2] if p[1] else None


def p_where_opt(p):
    r"""from_opt : WHERE boolean_expression | empty"""
    return p[2] if p[1] else None


def p_group_by_opt(p):
    r"""group_by_opt : GROUP BY set_quantifier_opt grouping_elements | empty"""
    return p[3] if p[1] else None


def p_having_opt(p):
    r"""from_opt : HAVING boolean_expression | empty"""
    return p[2] if p[1] else None


def p_select_items(p):
    r"""select_items : select_item | select_items COMMA select_item"""
    _item_list(p)


def p_grouping_elements(p):
    r"""grouping_elements : grouping_element | grouping_elements COMMA grouping_element"""
    _item_list(p)

    ## """grouping_element : grouping_expressions                                               #singleGroupingSet"""

    ## """grouping_expressions
    ##     : '(' (expression (',' expression)*)? ')'
    ##     | expression"""

    ## """groupingSet
    ##     : '(' (qualified_name (',' qualified_name)*)? ')'
    ##     | qualified_name"""

    ## """named_query
    ##     : name=identifier (column_aliases)? AS '(' query ')'"""

def p_set_quantifier_opt(p):
    r"""set_quantifier : DISTINCT | ALL | empty"""
    p[0] = p[1] 
    

    ## """select_item
    ##     : expression (AS? identifier)?  #selectSingle
    ##     | qualified_name '.' ASTERISK    #selectAll
    ##     | ASTERISK                      #selectAll"""

    ## """relation
    ##     : join_type JOIN relation join_criteria | aliased_relation           #joinRelation"""

    ## """join_type
    ##     : INNER?
    ##     | LEFT OUTER?
    ##     | RIGHT OUTER?
    ##     | FULL OUTER?"""


    ## """join_criteria
    ##     : ON boolean_expression
    ##     | USING '(' identifier (',' identifier)* ')'"""

    ## """aliased_relation
    ##     : relationPrimary (AS? identifier column_aliases?)?"""

    ## """column_aliases
    ##     : '(' identifier (',' identifier)* ')'"""

    ## """relationPrimary
    ##     : qualified_name                                                   #tableName
    ##     | '(' query ')'                                                   #subqueryRelation
    ##     | '(' relation ')'                                                #parenthesizedRelation
    ##     """

    ## """espressions: expression | expressions COMMA expression

    ## """expression : boolean_expression"""


    ## """boolean_expression
    ##     : or_expression                                    #booleanDefault
    ##     | boolean_expression AND or_expression             #logicalBinary

    ## """or_expression
    ##     : simple_expression                                #booleanDefault
    ##     | or_expression OR simple_expression               #logicalBinary

    ## """simple_expression
    ##     : predicated                                                   #booleanDefault
    ##     | NOT boolean_expression                                        #logicalNot
    ##     | EXISTS '(' query ')'                                         #exists"""

    ## """predicated
    ##     : value_expression predicate[$value_expression.ctx]?"""

    ## """predicate[ParserRuleContext value]
    ##     : comparisonOperator right=value_expression                            #comparison
    ##     | NOT? BETWEEN lower=value_expression AND upper=value_expression        #between
    ##     | NOT? IN '(' expression (',' expression)* ')'                        #inList
    ##     | NOT? IN '(' query ')'                                               #inSubquery
    ##     | NOT? LIKE pattern=value_expression (ESCAPE escape=value_expression)?  #like
    ##     | IS NOT? NULL                                                        #nullPredicate
    ##     | IS NOT? DISTINCT FROM right=value_expression                         #distinctFrom"""

    ## """value_expression
    ##     : primaryExpression                                                                 #value_expressionDefault
    ##     | value_expression AT timezone_specifier                                              #atTimeZone
    ##     | operator=(MINUS | PLUS) value_expression                                           #arithmeticUnary
    ##     | left=value_expression operator=(ASTERISK | SLASH | PERCENT) right=value_expression  #arithmeticBinary
    ##     | left=value_expression operator=(PLUS | MINUS) right=value_expression                #arithmeticBinary
    ##     | left=value_expression CONCAT right=value_expression                                 #concatenation"""

    ## """primaryExpression
    ##     : NULL                                                                           #nullLiteral
    ##     | interval                                                                       #intervalLiteral
    ##     | identifier STRING                                                              #typeConstructor
    ##     | number                                                                         #numericLiteral
    ##     | booleanValue                                                                   #booleanLiteral
    ##     | STRING                                                                         #stringLiteral
    ##     | BINARY_LITERAL                                                                 #binaryLiteral
    ##     | POSITION '(' value_expression IN value_expression ')'                            #position
    ##     | '(' expression (',' expression)+ ')'                                           #rowConstructor
    ##     | ROW '(' expression (',' expression)* ')'                                       #rowConstructor
    ##     | qualified_name '(' ASTERISK ')'                                            #functionCall
    ##     | qualified_name '(' (    set_quantifier_opt expression (',' expression)*)? ')'     #functionCall
    ##     | identifier '->' expression                                                     #lambda
    ##     | '(' identifier (',' identifier)* ')' '->' expression                           #lambda
    ##     | '(' query ')'                                                                  #subqueryExpression
    ##     | CASE value_expression whenClause+ (ELSE elseExpression=expression)? END         #simpleCase
    ##     | CASE whenClause+ (ELSE elseExpression=expression)? END                         #searchedCase
    ##     | CAST '(' expression AS type ')'                                                #cast
    ##     | TRY_CAST '(' expression AS type ')'                                            #cast
    ##     | ARRAY '[' (expression (',' expression)*)? ']'                                  #arrayConstructor
    ##     | value=primaryExpression '[' index=value_expression ']'                          #subscript
    ##     | identifier                                                                     #columnReference
    ##     | base=primaryExpression '.' fieldName=identifier                                #dereference
    ##     | name=CURRENT_DATE                                                              #specialDateTimeFunction
    ##     | name=CURRENT_TIME ('(' precision=INTEGER_VALUE ')')?                           #specialDateTimeFunction
    ##     | name=CURRENT_TIMESTAMP ('(' precision=INTEGER_VALUE ')')?                      #specialDateTimeFunction
    ##     | name=LOCALTIME ('(' precision=INTEGER_VALUE ')')?                              #specialDateTimeFunction
    ##     | name=LOCALTIMESTAMP ('(' precision=INTEGER_VALUE ')')?                         #specialDateTimeFunction
    ##     | SUBSTRING '(' value_expression FROM value_expression (FOR value_expression)? ')'  #substring
    ##     | NORMALIZE '(' value_expression (',' normalForm)? ')'                            #normalize
    ##     | EXTRACT '(' identifier FROM value_expression ')'                                #extract
    ##     | '(' expression ')'                                                             #parenthesizedExpression"""

    ## """timezone_specifier
    ##     : TIME ZONE interval  #timeZoneInterval
    ##     | TIME ZONE STRING    #timeZoneString"""

    ## comparisonOperator
    ##     : EQ | NEQ | LT | LTE | GT | GTE

    ## booleanValue
    ##     : TRUE | FALSE

    ## interval
    ##     : INTERVAL sign=(PLUS | MINUS)? STRING from=intervalField (TO to=intervalField)?

    ## intervalField
    ##     : YEAR | MONTH | DAY | HOUR | MINUTE | SECOND


def p_table_element(p):
    """table_element : IDENTIFIER type"""
    p[0] = TableElement(line=p.lineno(1), pos=p.lexpos(1), name=p[1], typedef=p[2])


def p_type(p):
    """type : base_type type_parameter_opt"""
    p[0] = "%s%s" % (p[1], p[2] or '')


def p_type_parameter_opt(p):
    """type_parameter_opt : LPAREN INTEGER RPAREN
                          | empty"""
    p[0] = "(%s)" % p[2] if p[1] else None


def p_base_type(p):
    """base_type : IDENTIFIER"""
    p[0] = p[1]



# p_type

# p_type_parameter_opt

# p_base_type

    ## whenClause
    ##     : WHEN condition=expression THEN result=expression


    ## explain_option
    ##     : FORMAT value=(TEXT | GRAPHVIZ)         #explainFormat
    ##     | TYPE value=(LOGICAL | DISTRIBUTED)     #explainType


    ## transactionMode
    ##     : ISOLATION LEVEL levelOfIsolation    #isolationLevel
    ##     | READ accessMode=(ONLY | WRITE)      #transactionAccessMode

    ## levelOfIsolation
    ##     : READ UNCOMMITTED                    #readUncommitted
    ##     | READ COMMITTED                      #readCommitted
    ##     | REPEATABLE READ                     #repeatableRead
    ##     | SERIALIZABLE                        #serializable

    ## callArgument
    ##     : expression                    #positionalArgument
    ##     | identifier '=>' expression    #namedArgument

    ## qualified_name
    ##     : identifier ('.' identifier)*

    ## identifier
    ##     : IDENTIFIER             #unquotedIdentifier
    ##     | quotedIdentifier       #quotedIdentifierAlternative
    ##     | nonReserved            #unquotedIdentifier
    ##     | BACKQUOTED_IDENTIFIER  #backQuotedIdentifier
    ##     | DIGIT_IDENTIFIER       #digitIdentifier

    ## quotedIdentifier
    ##     : QUOTED_IDENTIFIER

    ## number
    ##     : DECIMAL_VALUE  #decimalLiteral
    ##     | INTEGER_VALUE  #integerLiteral


    ## normalForm
    ##     : NFD | NFC | NFKD | NFKC


    ## IF: 'IF';
    ## NULLIF: 'NULLIF';
    ## COALESCE: 'COALESCE';

    ## EQ  : '=';
    ## NEQ : '<>' | '!=';
    ## LT  : '<';
    ## LTE : '<=';
    ## GT  : '>';
    ## GTE : '>=';

    ## PLUS: '+';
    ## MINUS: '-';
    ## ASTERISK: '*';
    ## SLASH: '/';
    ## PERCENT: '%';
    ## CONCAT: '||';

    ## STRING
    ##     : '\'' ( ~'\'' | '\'\'' )* '\''
    ##     ;

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

print "1:"
print parser.parse("Foo INTEGER", tracking=True)
#print parser.parse("Name INTEGER(1)", tracking=True)
print "2:"
print parser.parse("Bar Double(123)", tracking=True)
