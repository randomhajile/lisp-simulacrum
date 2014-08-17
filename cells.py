class Nil:
    """A class that is used to implement nil. I would prefer this to be a
    singleton, but it doesn't really cause any problems as is."""
    def __init__(self):
        self.islist = True
        self.lexval = 'nil'

    def listp(self):
        return True

    def __repr__(self):
        return 'nil'

    def __nonzero__(self):
        return True

class Cell:
    """A cell basically a cons cell from lisp. All list processing
    functions, e.g. car, cadr, and cdadr are methods."""
    def __init__(self, first, rest):
        """The attribute names here are somewhat misleading. You can put
        anything in the 'rest' field, not just a list. This would lead to an
        improper list, but it's still a valid Cell."""
        self.first = first
        self.rest = rest

    def __repr__(self):
        if self.islist():
            res = '(' + self.first.__repr__()
            n = self.rest
            while type(n) != Nil:
                res += ' ' + n.first.__repr__()
                n = n.rest
            res += ')'
            return res
        else:
            return '(' + self.first.__repr__() + ' . ' + self.rest.__repr__() + ')'

    def islist(self):
        """Within this class, this is mostly used for printing. E.g. an
        'improper' list like (1 2 . 3) should be printed as such. This is also
        used to implement the 'list?' primitive."""
        if type(self.rest) == Nil:
            return True
        elif type(self.rest) == Cell and self.rest.islist():
            return True
        else:
            return False

    def car(self):
        return self.first

    def cdr(self):
        return self.rest

    def caar(self):
        return self.car().car()

    def cadr(self):
        return self.cdr().car()

    def cdar(self):
        return self.car().cdr()

    def cddr(self):
        return self.cdr().cdr()

    def caaar(self):
        return self.car().car().car()

    def caadr(self):
        return self.cdr().car().car()

    def cadar(self):
        return self.car().cdr().car()

    def cdaar(self):
        return self.car().car().cdr()

    def caddr(self):
        return self.cdr().cdr().car()

    def cdadr(self):
        return self.cdr().car().cdr()

    def cddar(self):
        return self.car().cdr().cdr()

    def cdddr(self):
        return self.cdr().cdr().cdr()
