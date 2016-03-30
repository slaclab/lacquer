from ply import lex, yacc

from .reserved import *

reserved = sorted(set(presto_tokens).difference(presto_nonreserved).intersection(sql92_reserved))

tokens = ['INTEGER',    'DECIMAL',
          'IDENTIFIER', 'STRING',
          'COMMA',      'SEMI',
          'PLUS',       'MINUS',
          'TIMES',      'DIVIDE',
          'LPAREN',     'RPAREN',
          'GT',         'GE',
          'LT',         'LE',
          'EQ',         'NE', 
          ] + list(reserved)

_exponent = r'[eE][+-]?\d+'
_flit1 = r'\d+\.\d*'
_flit2 = r'\.\d+'
_flit3 = r'\d+'
_flits = '|'.join([_flit1, _flit2, _flit3])
t_INTEGER = r'\d+'
t_DECIMAL = r'[-]?({flits})({exp})?'.format(exp=_exponent, flits=_flits)


def t_IDENTIFIER(t):
    r"""[a-zA-Z_][a-zA-Z0-9_@:]*"""
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lex.lex()

def loc(p, idx):
    return dict(line=p.lineno(idx), pos=p.lexpos(1))

class Anode:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return repr(self.__dict__)

def p_table_element(p):
    """table_element : IDENTIFIER type"""
    _loc = loc(p, 1)
    identifier = p[1]
    typedef = p[2]
    p[0] = Anode(name=identifier, typedef=typedef, **loc(p, 1))

def p_type(p):
    """type : base_type type_parameter_opt"""
    _loc = loc(p, 1)
    base_type = p[1]
    type_parameter_opt = p[2]
    p[0] = Anode(type=p[1], type_parameter=p[2], **loc(p, 1))

def p_type_parameter_opt(p):
    """type_parameter_opt : LPAREN INTEGER RPAREN
                          | empty"""
    _loc = loc(p, 1) if p[1] else None
    p[0] =  Anode(pos=_loc['pos'], line=_loc['pos'], size=p[2]) if _loc else None

def p_base_type(p):
    """base_type : IDENTIFIER"""
    p[0] = p[1]

def p_empty(p):
    'empty :'
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



#def p_table_properties(p):
#    """table_properties : '(' table_property (',' table_property)* ')'"""
#    return TableProperties(p


    ## """table_property : identifier EQ expression"""
    
    ## """query_term
    ##     : query_primary                                                             #query_termDefault
    ##     | left=query_term operator=INTERSECT set_quantifier? right=query_term         #setOperation
    ##     | left=query_term operator=(UNION | EXCEPT) set_quantifier? right=query_term  #setOperation"""
    
    ## """query_primary
    ##     : query_specification                   #query_primaryDefault
    ##     | TABLE qualified_name                  #table
    ##     | VALUES expression (',' expression)*  #inlineTable
    ##     | '(' query  ')'                 #subquery"""
    
    ## """query:
    ##       query_term
    ##       (ORDER BY sort_item (',' sort_item)*)?
    ##       (LIMIT limit=(INTEGER_VALUE | ALL))?"""
    
    ## """sort_item
    ##     : expression ordering=(ASC | DESC)? (NULLS null_ordering=(FIRST | LAST))?"""
    
    ## """query_specification
    ##     : SELECT set_quantifier? select_item (',' select_item)*
    ##       (FROM relation (',' relation)*)?
    ##       (WHERE where=boolean_expression)?
    ##       (GROUP BY grouping_element (',' grouping_element)*)?
    ##       (HAVING having=boolean_expression)?"""
    
    ## """grouping_element : grouping_expressions                                               #singleGroupingSet"""
    
    ## """grouping_expressions
    ##     : '(' (expression (',' expression)*)? ')'
    ##     | expression"""
    
    ## """groupingSet
    ##     : '(' (qualified_name (',' qualified_name)*)? ')'
    ##     | qualified_name"""
    
    ## """named_query
    ##     : name=identifier (column_aliases)? AS '(' query ')'"""
    
    ## """set_quantifier
    ##     : DISTINCT
    ##     | ALL"""
    
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
    ##     | qualified_name '(' (set_quantifier? expression (',' expression)*)? ')'     #functionCall
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
    
    ## nonReserved
    ##     : SHOW | TABLES | COLUMNS | COLUMN | FUNCTIONS | SCHEMAS | CATALOGS | SESSION
    ##     | ADD
    ##     | ROWS | PRECEDING | FOLLOWING | CURRENT | ROW | MAP | ARRAY
    ##     | DATE | TIME | TIMESTAMP | INTERVAL | ZONE
    ##     | YEAR | MONTH | DAY | HOUR | MINUTE | SECOND
    ##     | EXPLAIN | FORMAT | TYPE | TEXT | GRAPHVIZ | LOGICAL | DISTRIBUTED
    ##     | TABLESAMPLE | SYSTEM | USE | TO
    ##     | RESCALED | APPROXIMATE | AT | CONFIDENCE
    ##     | SET | RESET
    ##     | VIEW | REPLACE
    ##     | IF | NULLIF | COALESCE
    ##     | normalForm
    ##     | POSITION
    ##     | NO | DATA
    ##     | START | TRANSACTION | COMMIT | ROLLBACK | WORK | ISOLATION | LEVEL
    ##     | SERIALIZABLE | REPEATABLE | COMMITTED | UNCOMMITTED | READ | WRITE | ONLY
    ##     | CALL
    
    ## normalForm
    ##     : NFD | NFC | NFKD | NFKC
    
    ## SELECT: 'SELECT';
    ## FROM: 'FROM';
    ## ADD: 'ADD';
    ## AS: 'AS';
    ## ALL: 'ALL';
    ## SOME: 'SOME';
    ## ANY: 'ANY';
    ## DISTINCT: 'DISTINCT';
    ## WHERE: 'WHERE';
    ## GROUP: 'GROUP';
    ## BY: 'BY';
    ## GROUPING: 'GROUPING';
    ## SETS: 'SETS';
    ## CUBE: 'CUBE';
    ## ROLLUP: 'ROLLUP';
    ## ORDER: 'ORDER';
    ## HAVING: 'HAVING';
    ## LIMIT: 'LIMIT';
    ## APPROXIMATE: 'APPROXIMATE';
    ## AT: 'AT';
    ## CONFIDENCE: 'CONFIDENCE';
    ## OR: 'OR';
    ## AND: 'AND';
    ## IN: 'IN';
    ## NOT: 'NOT';
    ## NO: 'NO';
    ## EXISTS: 'EXISTS';
    ## BETWEEN: 'BETWEEN';
    ## LIKE: 'LIKE';
    ## IS: 'IS';
    ## NULL: 'NULL';
    ## TRUE: 'TRUE';
    ## FALSE: 'FALSE';
    ## NULLS: 'NULLS';
    ## FIRST: 'FIRST';
    ## LAST: 'LAST';
    ## ESCAPE: 'ESCAPE';
    ## ASC: 'ASC';
    ## DESC: 'DESC';
    ## SUBSTRING: 'SUBSTRING';
    ## POSITION: 'POSITION';
    ## FOR: 'FOR';
    ## DATE: 'DATE';
    ## TIME: 'TIME';
    ## TIMESTAMP: 'TIMESTAMP';
    ## INTERVAL: 'INTERVAL';
    ## YEAR: 'YEAR';
    ## MONTH: 'MONTH';
    ## DAY: 'DAY';
    ## HOUR: 'HOUR';
    ## MINUTE: 'MINUTE';
    ## SECOND: 'SECOND';
    ## ZONE: 'ZONE';
    ## CURRENT_DATE: 'CURRENT_DATE';
    ## CURRENT_TIME: 'CURRENT_TIME';
    ## CURRENT_TIMESTAMP: 'CURRENT_TIMESTAMP';
    ## LOCALTIME: 'LOCALTIME';
    ## LOCALTIMESTAMP: 'LOCALTIMESTAMP';
    ## EXTRACT: 'EXTRACT';
    ## CASE: 'CASE';
    ## WHEN: 'WHEN';
    ## THEN: 'THEN';
    ## ELSE: 'ELSE';
    ## END: 'END';
    ## JOIN: 'JOIN';
    ## CROSS: 'CROSS';
    ## OUTER: 'OUTER';
    ## INNER: 'INNER';
    ## LEFT: 'LEFT';
    ## RIGHT: 'RIGHT';
    ## FULL: 'FULL';
    ## NATURAL: 'NATURAL';
    ## USING: 'USING';
    ## ON: 'ON';
    ## ROWS: 'ROWS';
    ## UNBOUNDED: 'UNBOUNDED';
    ## PRECEDING: 'PRECEDING';
    ## FOLLOWING: 'FOLLOWING';
    ## CURRENT: 'CURRENT';
    ## ROW: 'ROW';
    ## WITH: 'WITH';
    ## RECURSIVE: 'RECURSIVE';
    ## VALUES: 'VALUES';
    ## CREATE: 'CREATE';
    ## TABLE: 'TABLE';
    ## VIEW: 'VIEW';
    ## REPLACE: 'REPLACE';
    ## INSERT: 'INSERT';
    ## DELETE: 'DELETE';
    ## INTO: 'INTO';
    ## CONSTRAINT: 'CONSTRAINT';
    ## DESCRIBE: 'DESCRIBE';
    ## EXPLAIN: 'EXPLAIN';
    ## FORMAT: 'FORMAT';
    ## TYPE: 'TYPE';
    ## TEXT: 'TEXT';
    ## GRAPHVIZ: 'GRAPHVIZ';
    ## LOGICAL: 'LOGICAL';
    ## DISTRIBUTED: 'DISTRIBUTED';
    ## CAST: 'CAST';
    ## TRY_CAST: 'TRY_CAST';
    ## SHOW: 'SHOW';
    ## TABLES: 'TABLES';
    ## SCHEMAS: 'SCHEMAS';
    ## CATALOGS: 'CATALOGS';
    ## COLUMNS: 'COLUMNS';
    ## COLUMN: 'COLUMN';
    ## USE: 'USE';
    ## PARTITIONS: 'PARTITIONS';
    ## FUNCTIONS: 'FUNCTIONS';
    ## DROP: 'DROP';
    ## UNION: 'UNION';
    ## EXCEPT: 'EXCEPT';
    ## INTERSECT: 'INTERSECT';
    ## TO: 'TO';
    ## SYSTEM: 'SYSTEM';
    ## TABLESAMPLE: 'TABLESAMPLE';
    ## RESCALED: 'RESCALED';
    ## STRATIFY: 'STRATIFY';
    ## ALTER: 'ALTER';
    ## RENAME: 'RENAME';
    ## ORDINALITY: 'ORDINALITY';
    ## ARRAY: 'ARRAY';
    ## MAP: 'MAP';
    ## SET: 'SET';
    ## RESET: 'RESET';
    ## SESSION: 'SESSION';
    ## DATA: 'DATA';
    ## START: 'START';
    ## TRANSACTION: 'TRANSACTION';
    ## COMMIT: 'COMMIT';
    ## ROLLBACK: 'ROLLBACK';
    ## WORK: 'WORK';
    ## ISOLATION: 'ISOLATION';
    ## LEVEL: 'LEVEL';
    ## SERIALIZABLE: 'SERIALIZABLE';
    ## REPEATABLE: 'REPEATABLE';
    ## COMMITTED: 'COMMITTED';
    ## UNCOMMITTED: 'UNCOMMITTED';
    ## READ: 'READ';
    ## WRITE: 'WRITE';
    ## ONLY: 'ONLY';
    ## CALL: 'CALL';
    
    ## NORMALIZE: 'NORMALIZE';
    ## NFD : 'NFD';
    ## NFC : 'NFC';
    ## NFKD : 'NFKD';
    ## NFKC : 'NFKC';
    
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
    
    ## INTEGER_VALUE
    ##     : DIGIT+
    ##     ;
    
    ## DECIMAL_VALUE
    ##     : DIGIT+ '.' DIGIT*
    ##     | '.' DIGIT+
    ##     | DIGIT+ ('.' DIGIT*)? EXPONENT
    ##     | '.' DIGIT+ EXPONENT
    ##     ;
    
    ## IDENTIFIER
    ##     : (LETTER | '_') (LETTER | DIGIT | '_' | '@' | ':')*
    ##     ;
    
    ## DIGIT_IDENTIFIER
    ##     : DIGIT (LETTER | DIGIT | '_' | '@' | ':')+
    ##     ;
    
    ## QUOTED_IDENTIFIER
    ##     : '"' ( ~'"' | '""' )* '"'
    ##     ;
    
    ## BACKQUOTED_IDENTIFIER
    ##     : '`' ( ~'`' | '``' )* '`'
    ##     ;
    
    ## TIME_WITH_TIME_ZONE
    ##     : 'TIME' WS 'WITH' WS 'TIME' WS 'ZONE'
    ##     ;
    
    ## TIMESTAMP_WITH_TIME_ZONE
    ##     : 'TIMESTAMP' WS 'WITH' WS 'TIME' WS 'ZONE'
    ##     ;
    
    ## fragment EXPONENT
    ##     : 'E' [+-]? DIGIT+
    ##     ;
    
    ## fragment DIGIT
    ##     : [0-9]
    ##     ;
    
    ## fragment LETTER
    ##     : [A-Z]
    ##     ;
    
    ## SIMPLE_COMMENT
    ##     : '--' ~[\r\n]* '\r'? '\n'? -> channel(HIDDEN)
    ##     ;
    
    ## BRACKETED_COMMENT
    ##     : '/*' .*? '*/' -> channel(HIDDEN)
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
