from parser import *
from cells import *
from env import *
from evaluator import *
from lexer import *
from tokens import *
from time import time

class Reader:
    def __init__(self, parser=None, evaluator=None, lexer=None):
        if parser is None:
            self.parser = Parser()
        else:
            self.parser = parser
        if evaluator is None:
            self.evaluator = Evaluator()
        else:
            self.evaluator = evaluator
        if lexer is None:
            self.lexer = Lexer()
        else:
            self.lexer = lexer

    def read(self):
        res = ''
        lparens = 0
        rparens = 0
        try:
            res += input('>>')
        except EOFError:
            exit('\nBye for now!')
        lparens = res.count('(')
        rparens = res.count(')')
        while lparens > rparens:
            try:
                res += '\n' + input() #newlines are important for comments
            except EOFError:
                exit('\nBye for now!')
            lparens = res.count('(')
            rparens = res.count(')')
        res = self.process(res)
        return res

    def process(self, s):
        tokens = self.lexer.tokenize(s)
        cells = self.parser.parse(tokens)
        return cells

    def eval(self, c):
        return self.evaluator.eval(c)

    def printer(self, token):
        """Doesn't print out very pretty stuff for functions. Make that
        go away eventually."""
        if type(token) == Cell:
            c = token.car()
            if type(c) == ID and c.lexval == 'procedure':
                print('<procedure>')
            elif type(c) == ID and c.lexval == 'macro':
                print('<macro>')
            else:
                print(token)
        else:
            print(token)

    def repl(self, debug=False):
        while True:
            try:
                r = self.read()
            except ParseError as X:
                print(X)
                continue
            # for exp in r:
            #     e = self.eval(exp)
            if not r:
                continue
            try:
                for exp in r:
                    e = self.eval(exp)
            except (NameError, LexError, ApplyError, EvalError, ParseError) as X:
                print(X)
                continue
            except RuntimeError:
                print('Too much recursion!')
                continue
            except TypeError as X:
                print(X)
                continue
            except AttributeError as X:
                print(X)
                continue
            self.printer(e)

if __name__ == '__main__':
    from primitives import *
    env = Environment(table={k: ID(k) for k in primitives})
    E = Evaluator(env=env, primitiveprocedures=primitives)
    R = Reader(evaluator=E)
    with open('builtins.l', 'r') as f:
        builtins = R.process(f.read())
        for exp in builtins:
            R.eval(exp)
    R.repl()
