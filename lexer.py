from env import *
from tokens import *
import re

class LexError(Exception):
    pass

class Lexer:
    def __init__(self):
        pass

    def isdelim(self, c):
        """We allow None as a delimiter because that will be the EOF delimiter."""
        r =  c is None or c.isspace() or c in '()[]";#\0'
        return r

    def getchar(self):
        try:
            self.char = self.instring[0]
            self.instring = self.instring[1:]
        except IndexError:
            self.char = None

    def tokenize(self, instring):
        self.instring = instring
        self.getchar()
        tokens = []
        while self.char:
            tokens.append(self.gentoken())
            self.getchar()
        return tokens

    def gentoken(self):
        incomment = False
        if self.char == ';':
            incomment = True
        while self.char and (self.char.isspace() or incomment):
            self.getchar()
            if self.char == '\n' and incomment:
                incomment = False
                self.getchar()
            elif self.char == ';' and not incomment:
                incomment = True
        if self.char == '(':
            return LParen()
        elif self.char == ')':
            return RParen()
        elif self.char == '[':
            return LBrack()
        elif self.char == ']':
            return RBrack()
        elif self.char == '\'':
            return Quote()
        elif self.char == '`':
            return BQuote()
        elif self.char == '"':
            self.getchar()
            s = '"'
            while self.char != '"':
                s += self.char
                self.getchar()
            s += '"'
            return String(s)
        elif self.char == '#':
            self.getchar()
            if self.char == 't' or self.char == 'T':
                return ID('#t')
            elif self.char == 'f' or self.char == 'F':
                return ID('#f')
        elif self.char == ',':
            n = self.instring[0]
            if n == '@':
                self.getchar()
                return UnSyntaxSplicing()
            else:
                return Comma()
        elif self.char is not None:
            ## number or identifier
            return self.getnum()

    def getnum(self):
        ## can't use getchar for a bit...
        pos = 0
        hasdec = False
        hasexp = False
        ## this is ugly, and I shouldn't have to do it. make it better.
        self.instring = self.char + self.instring
        c = self.instring[pos]
        
        while not self.isdelim(c):
            if not c.isdigit():
                if c == '.':
                    if not hasdec:
                        hasdec = True
                        pos += 1
                        try:
                            c = self.instring[pos]
                        except IndexError:
                            c = None #2. is okay.
                        continue
                elif c in 'eE':
                    hasexp = True
                    pos += 1
                    try:
                        c = self.instring[pos]
                    except IndexError:
                        return self.getid() #2e is not okay, it is an ID.
                    if c in '-+' or c.isdigit():
                        pos += 1
                        try:
                            c = self.instring[pos]
                        except IndexError:
                            return self.getid() #2e+ is also an id
                        continue
                return self.getid()
            pos += 1
            try:
                c = self.instring[pos]
            except IndexError:
                c = None
        lexval = self.instring[:pos]
        self.instring = self.instring[pos:]
        if hasdec:
            return Float(lexval)
        else:
            return Int(lexval)

    def getid(self):
        pos = 0
        c = self.instring[pos]
        while not self.isdelim(c):
            pos += 1
            try:
                c = self.instring[pos]
            except IndexError:
                c = None
        lexval = self.instring[:pos]
        self.instring = self.instring[pos:]

        return ID(lexval)

if __name__ == '__main__':
    L = Lexer()
    s = """(define (fib-iter n a b)
 (if (= n 0)
   a
     (fib-iter (- n 1) b (+ a b))))"""
    t = L.tokenize(s)
    print(t)
