from tokens import *
from cells import *

bfltrue = ID('#t')
bflfalse = ID('#f')

### All methods that return a list had to be modified with the inclusion of TCO
### if you want (x1 ... xn) to be returned then you have to return something like
### (quote (x1 ... nx)), when the evaluator gets it, it will return (x1 ... xn).

def car(cell):
    return Cell(ID('quote'), Cell(cell.car(), Nil()))
    #return cell.car()

def cdr(cell):
    return Cell(ID('quote'), Cell(cell.cdr(), Nil()))
    #return cell.cdr()

def cons(item1, item2):
    return Cell(ID('quote'), Cell(Cell(item1, item2), Nil()))
    #return Cell(item1, item2)

def listp(x):
    if type(x) == Nil or (type(x) == Cell and x.islist()):
        return bfltrue
    else:
        return bflfalse

def buildlist(*items):
    if not items:
        return Nil()
    res = Cell(ID('quote'), Cell(Cell(items[0], Nil()), Nil()))
    nextcell = res.rest.first
    for x in items[1:]:
        nextcell.rest = Cell(x, Nil())
        nextcell = nextcell.rest
    return res

def setcar(x, value):
    if type(x) != Cell:
        return String('Not a cons cell.')
    else:
        x.first = value
        return value

def setcdr(x, value):
    if type(x) != Cell:
        return String('Not a cons cell.')
    else:
        x.rest = value
        return value

def nullp(x):
    return bfltrue if type(x) == Nil else bflfalse

def pairp(x):
    return bfltrue if type(x) == Cell else bflfalse


def append(x, *y):
    if listp(x) == bflfalse:
        raise AttributeError('First argument is not a list.')
    if nullp(x) == bflfalse:
        ## make a res of x.
        trial = Cell(ID('quote'), Cell(Cell(None, None), Nil()))
        res = trial.rest.first
        #res = Cell(None, None)
        forward = res
        currentxcell = x
        while True:
            forward.first = currentxcell.first
            currentxcell = currentxcell.rest
            if type(currentxcell) == Nil:
                forward.rest = Nil() #forward is how we will get to the end of the res later.
                break
            forward.rest = Cell(None, None)
            forward = forward.rest
    else:
        trial = Cell(ID('quote'), Cell(Cell(None, None), Nil()))
        res = trial.rest.first
        #res = Cell(None, None)
        forward = res
    for item in y:
        if forward.first is not None:
            forward.rest = Cell(None, None)
            forward = forward.rest
        forward.first = item
    forward.rest = Nil()
    return trial
    return res

def basicplus(x, y):
    if x.toknum == 3 and y.toknum == 3:
        return Int(x.lexval + y.lexval)
    elif x.toknum == 19 or y.toknum == 19:
        return Float(x.lexval + y.lexval)
    else:
        raise TypeError('Unsupported type(s) for +: {} and {}'.format(type(x).__name__,
                                                                      type(y).__name__))

def basicmult(x, y):
    if x.toknum == 3 and y.toknum == 3:
        return Int(x.lexval * y.lexval)
    else:
        return Float(x.lexval + y.lexval)

def basicminus(x, y):
    if x.toknum == 3 and y.toknum == 3:
        return Int(x.lexval - y.lexval)
    else:
        return Float(x.lexval - y.lexval)

def negative(x):
    if x.toknum == 3:
        return Int(-x.lexval)
    else:
        return Float(-x.lexval)

def plus(*x):
    res = Int(0)
    for tok in x:
        res = basicplus(res, tok)
    return res

def mult(*x):
    res = Int(1)
    for tok in x:
        res = basicmult(res, tok)
    return res

def minus(*x):
    l = len(x)
    if l == 1:
        val = negative(x[0])
        return val
    else:
        return basicminus(x[0], plus(*x[1:]))

def div(x, y):
    if x.toknum == 3 and y.toknum == 3:
        return Int(x.lexval / y.lexval)
    else:
        return Float(x.lexval / y.lexval)

def lt(x, y):
    if x.lexval < y.lexval:
        return bfltrue
    else:
        return bflfalse

def lte(x, y):
    if x.lexval <= y.lexval:
        return bfltrue
        #return ID('#t')
    else:
        return bflfalse
        #return ID('#f')

def gt(x, y):
    if y.lexval < x.lexval:
        return bfltrue
    else:
        return bflfalse

def gte(x, y):
    if y.lexval <= x.lexval:
        return bfltrue
    else:
        return bflfalse

def neq(x, y):
    if x.lexval != y.lexval:
        return bfltrue
    else:
        return bflfalse

def eq(x, y):
    if x.lexval == y.lexval:
        return bfltrue
    else:
        return bflfalse

def zerop(x):
    if (type(x) == Int or type(x) == Float) and x.lexval == 0: # in python 0 == 0.0
        return bfltrue
    else:
        return bflfalse

def stringp(x):
    return bfltrue if type(x) == String else bflfalse

def stringlength(s):
    return Int(len(s.lexval)-2) #remove the DQuotes

def bflor(*items):
    for x in items:
        if x.lexval != bflfalse.lexval:
            return bfltrue
    return bflfalse

def bfland(*items):
    for x in items:
        if x.lexval == bflfalse.lexval:
            return bflfalse
    return bfltrue

def bflnot(x):
    if x.lexval == bflfalse.lexval:
        return bfltrue
    else:
        return bfltrue

def booleanp(x):
    if x.lexval == bfltrue or x.lexval == bflfalse:
        return bfltrue
    else:
        return bflfalse

def display(x):
    if type(x) == String:
        print(x.lexval.replace('"', ''), end='')
    elif type(x) == Cell:
        print(x, end='')
    else:
        print(x.lexval, end='')
    return bfltrue

def newline():
    print('\n', end='')
    return bfltrue

## You can completely bork functionality by redefining these in the interpreter.
## I should consider shielding them from the user, but it's more fun to let
## them be accessible.
primitives = {'car': car,
              'cdr': cdr,
              'cons': cons,
              'list?': listp,
              'list': buildlist,
              'set-car!': setcar,
              'set-cdr!': setcdr,
              'null?': nullp,
              'pair?': pairp,
              'append': append,
              '+': plus,
              '*': mult,
              '-': minus,
              '/': div,
              '<': lt,
              '<=': lte,
              '>': gt,
              '>=': gte,
              '=': eq,
              'zero?': zerop,
              'string?': stringp,
              'string-length': stringlength,
              'or': bflor,
              'and': bfland,
              'not': bflnot,
              'boolean?': booleanp,
              '#t': True,
              '#f': False,
              'display': display,
              'newline': newline}
