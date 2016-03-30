from ply import lex, yacc

reserved = {
#    'insert' : 'INSERT', 
#    'into'   : 'INTO',
    'select' : 'SELECT',
#    'from'   : 'FROM',
    'where'  : 'WHERE',
#    'order'  : 'ORDER',
#    'by'     : 'BY',
#    'values' : 'VALUES',
#    'and'    : 'AND',
#    'or'     : 'OR',
#    'not'    : 'NOT',
} 
    
tokens = ['INTEGER',
          'DECIMAL',
          'IDENTIFIER',
          'LPAREN',     'RPAREN'
#          'STRING',
#          'COMMA',      'SEMI',
#          'PLUS',       'MINUS',
#          'TIMES',      'DIVIDE',
#          'GT',         'GE',
#          'LT',         'LE',
#          'EQ',         'NE', 
          ] + list(reserved.values())

_exponent = r'[eE][+-]?\d+'
_flit1 = r'\d+\.\d*({exp})?'.format(exp=_exponent)
_flit2 = r'\.\d+({exp})?'.format(exp=_exponent)
_flit3 = r'\d+({exp})'.format(exp=_exponent) # require exponent
_flits = '|'.join([_flit1, _flit2, _flit3])

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_INTEGER = r'[-]?\d+'
t_DECIMAL = r'[-]?({flits})'.format(flits=_flits)
t_ignore  = ' \t'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_@:]*'
    val = t.value.lower()
    if val in reserved:
        t.type = reserved[val]
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()


def dump(string):
    print "lexing: " + string
    lexer.input(string)
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        print(tok)


dump("1")
dump("hell@ world 1")
dump("hello@world 1.23")
dump("hello:world -1.23")
dump("hello_world -1.23e12")
dump("hello_world -1.23e12")

#dump("select 1 from some_table")

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
    identifier = p[1]
    typedef = p[2]
    p[0] = Anode(name=identifier, typedef=typedef, **loc(p, 1))

def p_type(p):
    """type : base_type type_parameter_opt"""
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

