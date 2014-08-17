class Token:
    def __init__(self, lexval, toknum):
        """lexval is the actual string of symbols that the token represents.
        toknum is the number that the parser will read."""
        self.lexval = lexval
        self.toknum = toknum

    def __repr__(self):
        return str(self.lexval)

    ## useful for when you're testing and want to see legit tokens
    # def __repr__(self):
    #     res = []
    #     for x in [i for i in dir(self) if not i.startswith('__')]:
    #         res.append(x+'='+str(self.__getattribute__(x)))
    #     res = '<' + ', '.join(res) + '>'
    #     return res

class LParen(Token):
    def __init__(self):
        Token.__init__(self, '(', 0)

class RParen(Token):
    def __init__(self):
        Token.__init__(self, ')', 1)

class ID(Token):
    def __init__(self, lexval):
        Token.__init__(self, lexval, 2)

class Int(Token):
    def __init__(self, lexval):
        Token.__init__(self, int(lexval), 3)

class Quote(Token):
    def __init__(self):
        Token.__init__(self, "'", 4)

class DQuote(Token):
    def __init__(self):
        Token.__init__(self, '"', 5)

class BQuote(Token):
    def __init__(self):
        Token.__init__(self, '`', 6)

class Comma(Token):
    def __init__(self):
        Token.__init__(self, ',', 7)

class UnSyntaxSplicing(Token):
    def __init__(self):
        Token.__init__(self, ',@', 17)

class String(Token):
    def __init__(self, lexval):
        Token.__init__(self, lexval, 18)

class Float(Token):
    """Token number is so high because it was implemented later."""
    def __init__(self, lexval):
        Token.__init__(self, float(lexval), 19)

class GenSym(ID):
    def __init__(self):
        ID.__init__(self, 'gensym')
