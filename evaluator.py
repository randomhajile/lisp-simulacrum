from env import *
from cells import *
from tokens import *

class EvalError(Exception):
    pass

class ApplyError(Exception):
    pass

class Evaluator:
    def __init__(self, env=None, primitiveprocedures=None):
        self.gensymcounter = 0
        if env is None:
            self.env = Environment()
        else:
            self.env = env
        if primitiveprocedures is None:
            self.primitiveprocedures = {}
        else:
            self.primitiveprocedures = primitiveprocedures

    def eval(self, exp, env=None):
        """Attempt some TCO here. The idea is simple, eval everything until you
        get to the last expression, then you return."""
        self.gensymcounter += 1
        if env is None:
            env = self.env
        while True:
            if self.gensymp(exp):
                while 'gensym-' + str(self.gensymcounter) in env:
                    self.gensymcounter += 1
                return ID('gensym-'+str(self.gensymcounter))
            if self.selfevaluatingp(exp):
                return exp
            elif self.variablep(exp):
                return self.getvariablevalue(exp, env)
            elif self.quotedp(exp):
                return self.textofquotation(exp)
            elif self.assignmentp(exp):
                return self.evalassignment(exp, env)
            elif self.definitionp(exp):
                return self.evaldefinition(exp, env)
            elif self.bquotedp(exp):
                exp = self.walkcodeandreplace(exp.rest.first, env)
                return exp
            elif self.definemacrop(exp):
                macroname = exp.caadr()
                macroparams = exp.cdadr()
                macrobody = exp.caddr()
                self.definevariable(macroname, Cell(ID('macro'), Cell(macroparams, Cell(macrobody, Nil()))), env)
                return macroname
            elif self.letp(exp):
                bindings = self.letbindings(exp)
                body = exp.cddr()
                if self.nullp(body):
                    raise EvalError('Bad body')
                ## convert to a begin expression
                body = self.sequencetoexp(body)
                if not self.nullp(bindings):
                    letvars, letvals = self.bindingstolist(bindings, env)
                    env = Environment(dict(zip(letvars, letvals)), env)
                exp = body
            elif self.ifp(exp):
                exp = self.evalif(exp, env)
            elif self.lambdap(exp):
                return self.makeprocedure(self.lambdaparameters(exp),
                                          self.lambdabody(exp),
                                          env)
            elif self.beginp(exp):
                exp, env = self.evalsequence(self.beginactions(exp), env)
            elif self.condp(exp):
                self.eval(self.condtoif(exp), env)
            elif self.applicationp(exp):
                exp, env = self.apply(exp, env)
            else:
                raise EvalError('Unknown expression type-- EVAL {}'.format(exp.car()))

    def gensymp(self, p):
        return self.taggedlistp(p, 'gensym')

    def apply(self, exp, env):
        """This will be of the form (foo x1 ... xn) where foo can be one of the
        following types."""
        ##check if it's an apply first.
        if self.applyp(exp):
            return self.evalapply(exp, env)
        procedure = self.eval(exp.car(), env)
        if self.macrop(procedure):
            return self.evalmacro(exp, env)
        elif self.compoundprocedurep(procedure):
            return self.evalcompound(exp, env)
        elif self.primitiveprocedurep(procedure):
            return self.evalprimitive(exp, env)
        else:
            raise ApplyError('Unknown procedure type')

    def macrop(self, p):
        return self.taggedlistp(p, 'macro')

    def evalmacro(self, exp, env):
        """The goal here is to take the body of the macro, walk the code tree
        to commas and comma-ats and splice in the uneval'd args."""
        procedure = self.eval(self.operator(exp), env)
        args = exp.cdr()
        prevenv = env
        exp, env = self.evalsequence(procedure.cddr(),
                                     self.extendenvironment(procedure.cadr(),
                                                            args, env))
        exp = self.eval(exp, env)
        env = prevenv
        return exp, env

    def applyp(self, exp):
        return self.taggedlistp(exp, 'apply')

    def evalapply(self, exp, env):
        """exp should be of the form (apply proc list)"""
        procedure = self.eval(exp.cadr(), env)
        args = exp.caddr()
        if not type(args) == Cell:
            raise ApplyError('Apply expects a list -- APPLY {}'.format(args))
        if type(args.car()) in (Quote, BQuote):
            args = self.eval(args) ##now we just have a plain list of args
        else:
            args = self.eval(args, env)
        if self.compoundprocedurep(procedure):
            exp, env = self.evalsequence(self.procedurebody(procedure),
                                         self.extendenvironment(self.procedureparameters(procedure),
                                                                args, self.procedureenvironment(procedure)))
        elif self.primitiveprocedurep(procedure):
            exp = self.applyprimitiveprocedure(procedure, args)
        return exp, env

    def evalcompound(self, exp, env):
        """should be of the form (foo x1 ... xn)"""
        procedure = self.eval(self.operator(exp), env)
        args = self.listofvalues(self.operands(exp), env)
        exp, env = self.evalsequence(self.procedurebody(procedure),
                             self.extendenvironment(self.procedureparameters(procedure),
                                                    args, self.procedureenvironment(procedure)))
        return exp, env

    def evalprimitive(self, exp, env):
        procedure = self.eval(self.operator(exp), env)
        args = self.listofvalues(self.operands(exp), env)
        exp = self.applyprimitiveprocedure(procedure, args)
        return exp, env

    def listofvalues(self, exps, env):
        if self.nooperandsp(exps):
            return Nil()
        else:
            return Cell(self.eval(self.firstoperand(exps), env),
                        self.listofvalues(self.restoperands(exps), env))

    def evalif(self, exp, env):
        if self.bool(self.eval(self.ifpredicate(exp), env)):
            return self.ifconsequent(exp)
        else:
            return self.ifalternative(exp)

    def evalsequence(self, exps, env):
        if self.lastexpp(exps):
            return self.firstexp(exps), env
        else:
            self.eval(self.firstexp(exps), env)
            return self.evalsequence(self.restexps(exps), env)

    def evalassignment(self, exp, env):
        return self.setvariablevalue(self.assignmentvariable(exp),
                                     self.eval(self.assignmentvalue(exp), env),
                                     env)

    def evaldefinition(self, exp, env):
        return self.definevariable(self.definitionvariable(exp),
                                   self.eval(self.definitionvalue(exp), env),
                                   env)

    def selfevaluatingp(self, exp):
        if isinstance(exp, Cell):
            return False
        elif self.numberp(exp) or self.stringp(exp) or self.charp(exp):
            return True
        else:
            return False

    def variablep(self, exp):
        return self.symbolp(exp)

    def symbolp(self, exp):
        if not isinstance(exp, Token):
            return False
        else:
            return exp.toknum == 2

    def quotedp(self, exp):
        """Second part of conditional added after the fact, looks ugly."""
        return self.taggedlistp(exp, 'quote') or (type(exp.car()) != Cell and exp.car().toknum == 4)

    def applyp(self, exp):
        return self.taggedlistp(exp, 'apply')

    def letp(self, exp):
        return self.taggedlistp(exp, 'let')

    def letbindings(self, exp):
        return exp.cadr()

    def bindingstolist(self, bindings, env):
        bvars = []
        bvals = []
        while True:
            currentbinding = bindings.car()
            bvars.append(currentbinding.car().lexval) #only want the lexical value
            ## need to actually eval the args.
            bvals.append(self.eval(currentbinding.cadr(), env))
            if self.nullp(bindings.cdr()):
                break
            else:
                bindings = bindings.cdr()
        return bvars, bvals

    def genprocedurecall(self, exp, env):
        """Have to eval operands because it should be of the form
        (quote list)"""
        procedure = exp.cadr()
        operands = self.eval(exp.caddr(), env)
        #operands = self.listofvalues(exp.caddr(), env)
        #print(Cell(procedure, operands))
        return Cell(procedure, operands)

    def taggedlistp(self, exp, tag):
        if self.pairp(exp) and type(exp.car()) != Cell and exp.car().lexval == tag:
            return True
        else:
            return False

    def assignmentp(self, exp):
        return self.taggedlistp(exp, 'set!')

    def assignmentvariable(self, exp):
        return exp.cadr()

    def assignmentvalue(self, exp):
        return exp.caddr()

    def bquotedp(self, exp):
        return type(exp.car()) != Cell and exp.car().toknum == 6

    def walkcodeandreplace(self, exp, env):
        """We cannot mutate code here, that would be bad."""
        if type(exp) != Cell:
            res = exp
        elif type(exp.car()) == Comma:
            res = self.eval(exp.cdr().car(), env)
        elif type(exp.car()) == Cell and type(exp.car().car()) == UnSyntaxSplicing:
            ## you have to catch comma-at's in context of the parent expression.
            ## or you could schlep around the parent, either would work.
            tosplice = self.eval(exp.car().cdr().car(), env)
            if type(tosplice) != Cell or not tosplice.islist():
                raise SyntaxError('Comma-at expects a list, got {}'.format(tosplice))
            tail = tosplice
            while type(tail.rest) != Nil:
                tail = tail.rest
            res = tosplice
            tail.rest = self.walkcodeandreplace(exp.rest, env)
        else:
            res = Cell(None, None)
            res.first = self.walkcodeandreplace(exp.first, env)
            res.rest = self.walkcodeandreplace(exp.rest, env)
        return res

    def definemacrop(self, exp):
        return self.taggedlistp(exp, 'define-macro')

    def definitionp(self, exp):
        return self.taggedlistp(exp, 'define')

    def definitionvariable(self, exp):
        if self.symbolp(exp.cadr()):
            return exp.cadr()
        else:
            return exp.caadr()

    def definitionvalue(self, exp):
        if self.symbolp(exp.cadr()):
            return exp.caddr()
        else:
            return self.makelambda(exp.cdadr(), # params
                                   exp.cddr())  # body

    def lambdap(self, exp):
        return self.taggedlistp(exp, 'lambda')

    def lambdaparameters(self, exp):
        return exp.cadr()

    def lambdabody(self, exp):
        return exp.cddr()

    def makelambda(self, parameters, body):
        return Cell(ID('lambda'), Cell(parameters, body))

    def ifp(self, exp):
        return self.taggedlistp(exp, 'if')

    def ifpredicate(self, exp):
        return exp.cadr()

    def ifconsequent(self, exp):
        return exp.caddr()

    def ifalternative(self, exp):
        if not self.nullp(exp.cdddr()):
            return exp.cdddr().car() # I only implemented three deep.
        else:
            return False

    def makeif(self, predicate, consequent, alternative):
        return Cell(ID('if'), Cell(predicate, Cell(consequent, Cell(alternative, Nil()))))

    def beginp(self, exp):
        return self.taggedlistp(exp, 'begin')

    def beginactions(self, exp):
        return exp.cdr()

    def lastexpp(self, seq):
        return isinstance(seq.cdr(), Nil)

    def firstexp(self, seq):
        return seq.car()

    def restexps(self, seq):
        return seq.cdr()

    def sequencetoexp(self, seq):
        if isinstance(seq, Nil):
            return seq
        elif self.lastexpp(seq):
            return self.firstexp(seq)
        else:
            return self.makebegin(seq)

    def makebegin(self, seq):
        return Cell(ID('begin'), seq)

    def applicationp(self, exp):
        return isinstance(exp, Cell)

    def operator(self, exp):
        return exp.car()

    def operands(self, exp):
        return exp.cdr()

    def nooperandsp(self, ops):
        return isinstance(ops, Nil)

    def firstoperand(self, ops):
        return ops.car()

    def restoperands(self, ops):
        return ops.cdr()

    def condp(self, exp):
        return self.taggedlistp(exp, 'cond')

    def condclauses(self, exp):
        return exp.cdr()

    def condelseclausep(self, clause):
        return self.taggedlistp(clause, 'else')

    def condpredicate(self, clause):
         return clause.car()

    def condactions(self, clause):
        return clause.cdr()

    def condtoif(self, exp):
        return self.expandclauses(self.condclauses(exp))

    def expandclauses(self, clauses):
        if isinstance(clauses, Nil):
            return False
        else:
            first = clauses.car()
            rest = clauses.cdr()
            if self.condelseclausep(first):
                if isinstance(rest, Nil):
                    return self.sequencetoexp(self.condactions(first))
                else:
                    raise EvalError('Error, conditions after else clause.')
            return self.makeif(self.condpredicate(first),
                        self.sequencetoexp(self.condactions(first)),
                        self.expandclauses(rest))

    def bool(self, value):
        if value is False or value.lexval == '#f':
            return False
        else:
            return True

    def charp(self, x):
        return x.toknum == 14

    def stringp(self, x):
        return x.toknum == 18

    def numberp(self, x):
        return x.toknum == 3 or x.toknum == 19

    def nullp(self, x):
        return isinstance(x, Nil)

    def pairp(self, x):
        return isinstance(x, Cell)

    def primitiveprocedurep(self, procedure):
        return procedure.lexval in self.primitiveprocedures

    def makeprocedure(self, parameters, body, env):
        return Cell(ID('procedure'), Cell(parameters, Cell(body, Cell(env, Nil()))))

    def macrocallp(self, m):
        return self.taggedlistp(m, 'macro')

    def compoundprocedurep(self, p):
        return self.taggedlistp(p, 'procedure')

    def procedureparameters(self, p):
        return p.cadr()

    def procedurebody(self, p):
        return p.caddr()

    def procedureenvironment(self, p):
        return p.cdddr().car()

    def enclosingenvironment(self, env):
        return env.prev

    def emptyenvironment(self):
        return Env()

    def extendenvironment(self, variables, vals, baseenv):
        var = []
        val = []
        while True:
            x = self.nullp(variables)
            y = self.nullp(vals)
            if x and y:
                break
            elif x and not y:
                raise TypeError('Too many arguments')
            else:
                currentvar = variables.car().lexval
                exitloop = False
                if currentvar == '&optional':
                    variables = variables.cdr()
                    if type(variables) == Nil:
                        raise SyntaxError('Expected variable after &optional.')
                    currentvar = variables.car().lexval
                    while True:
                        x = self.nullp(variables)
                        y = self.nullp(vals)
                        if x and y: #end of params and args
                            exitloop = True
                            break
                        elif not x and y: #end of args, but not params
                            while True:
                                var.append(variables.car().lexval)
                                val.append(Nil())
                                tail = variables.cdr()
                                if type(tail) == Nil:
                                    break
                                variables = tail
                            exitloop = True
                            break
                        elif x and not y:
                            raise TypeError('Too few arguments.')
                        currentvar = variables.car().lexval
                        if currentvar == '&rest':
                            break
                        else:
                            currentval = vals.car()
                            var.append(currentvar)
                            val.append(currentval)
                            vals = vals.cdr()
                            variables = variables.cdr()
                if exitloop:
                    break
                if variables.car().lexval == '&rest':
                    variables = variables.cdr()
                    currentvar = variables.car().lexval
                    if not self.nullp(variables.cdr()):
                        raise SyntaxError('Expected null list in cdr after {}.'.format(currentvar))
                    var.append(currentvar)
                    val.append(vals)
                    break
                elif y:
                    raise TypeError('Too few arguments')
                else:
                    currentval = vals.car()
                    var.append(currentvar)
                    val.append(currentval)
                    variables = variables.cdr()
                    vals = vals.cdr()
        return Environment(dict(zip(var, val)), baseenv)

    def definevariable(self, variable, value, env):
        """This method simply immediately sets the variable to value in the
        given environment. Does not depend on __setval__ in the env class."""
        env.table[variable.lexval] = value
        return variable
        #return value

    def setvariablevalue(self, variable, value, env):
        """This attempts to find the variable in some containing environment
        and then sets its value to the associated value. If it doesn't find the
        variable, it raises an Exception."""
        currentframe = env
        while currentframe is not None:
            if variable.lexval in currentframe.table:
                currentframe.table[variable.lexval] = value
                return value
            else:
                currentframe = currentframe.prev
        else:
            raise Exception # what kind?

    def getvariablevalue(self, variable, env):
        return env[variable.lexval]

    def applyprimitiveprocedure(self, procedure, arguments):
        args = self.argstopylist(arguments)
        proc = self.primitiveprocedures[procedure.lexval]
        return proc(*args)

    def argstopylist(self, args):
        res = []
        while not self.nullp(args):
            res.append(args.car())
            args = args.cdr()
        return res

    def textofquotation(self, exp):
        return exp.cadr()

if __name__ == '__main__':
    from lexer import *
    from parser import *
    def car(cell):
        return cell.car()
    def cdr(cell):
        return cell.cdr()
    def cons(item1, item2):
        return Cell(item1, item2)
    def plus(x, y):
        return Num(x.lexval + y.lexval)
    def mult(x, y):
        return Num(x.lexval * y.lexval)
    def minus(x, y):
        return Num(x.lexval - y.lexval)
    def div(x, y):
        return Num(x.lexval / y.lexval)
    def lt(x, y):
        return x < y
    def lte(x, y):
        return x <= y
    def gt(x, y):
        return y < x
    def gte(x, y):
        return y <= x
    def neq(x, y):
        return x != y
    def eq(x, y):
        if x.lexval == y.lexval:
            return ID('#t')
        else:
            return ID('#f')
    primitives = {'car': car,
                  'cdr': cdr,
                  'cons': cons,
                  '+': plus,
                  '*': mult,
                  '-': minus,
                  '/': div,
                  '<': lt,
                  '<=': lte,
                  '>': gt,
                  '>=': gte,
                  '=': eq}
    env = Environment(table={'car': ID('car'),
                             'cdr': ID('cdr'),
                             'cons': ID('cons'),
                             '+': ID('+'),
                             '*': ID('*'),
                             '-': ID('-'),
                             '/': ID('/'),
                             'define': ID('define'),
                             '<': ID('<'),
                             '<=': ID('<='),
                             '>': ID('>'),
                             '>=': ID('>='),
                             '=': ID('=')})
    T = Lexer()
    P = Parser()
    def process(s):
        return P.parse(T.tokenize(s))
    s = '(define (plus1 x) (+ x 1))'
    E = Evaluator(env=env, primitiveprocedures=primitives)
    E.eval(process(s))
    print(E.eval(process('(plus1 1)')))
