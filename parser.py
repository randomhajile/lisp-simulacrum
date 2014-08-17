from cells import *

class ParseError(Exception):
    pass

class Parser:
    def parse(self, tokens):
        self.tokens = tokens
        res = []
        while self.tokens and self.tokens[0] is not None:
            res.append(self.S())
        return res
        
    def next(self):
        try:
            self.current = self.tokens.pop(0)
        except:
            self.current = None

    def S(self, getnext=True):
        if getnext:
            self.next()
        if self.current.toknum == 4 or self.current.toknum == 6: # added 6 for BQUOTE
            C = Cell(self.current, Cell(self.S(), Nil())) # quote takes precisely one s-expression
            return C
        elif self.current.toknum in [7, 17]: #splicing for macros
            C = Cell(self.current, Cell(self.S(), Nil()))
            return C
        if self.current.toknum == 0:
            self.next()
            if self.current.toknum == 1:
                return Nil()
            C = self.L(False)
            if self.current.toknum == 1:
                return C
            else:
                raise ParseError
        else:
            return self.current

    def L(self, getnext=True):
        if getnext:
            self.next()
        res = Cell(None, None)
        C = res
        P = res
        while True:
            C.first = self.S(False)
            self.next()
            if self.current.toknum == 1:
                C.rest = Nil()
                break
            else:
                new = Cell(None, None)
                C.rest = new
                C = new
        return res

if __name__ == '__main__':
    from lexer import *

    T = Lexer()
    t = T.tokenize("""(define (fib-iter n a b)
 (if (= n 0)
   a
     (fib-iter (- n 1) b (+ a b))))""")
    P = Parser()
    L = P.parse(t)
    print(L)
