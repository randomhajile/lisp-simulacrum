## Lisp Simulacrum ##
# Description #
This is a toy Lisp interpreter implemented in Python. I wanted to learn more about how
programming languages work and decided to make a mostly functional Lisp. The tokenizer
and parser are based on reading [Dragon Book](http://dragonbook.stanford.edu/)
with the lexer being an implementation of a FSA and the parser being a basic recursive-descent parser.
The evaluator was almost completely ripped from [SICP](https://mitpress.mit.edu/sicp/full-text/book/book.html),
with a nice tweak from Peter Norvig's [(An ((Even Better) Lisp) Interpreter (in Python))](http://norvig.com/lispy2.html), and a couple of my own ideas on application evaluation,
in particular, for `apply` and macros. Having said that, any bugs are entirely due to me.

This is nowhere near a production quality interpreter, but it's not too hard to understand
and might be useful as a learning tool. The style is not always super Pythonic, and
there are many places where I chose an approach closer to how I would implement in a
lower level language.

# Syntax and Not-So-Niceness #
The syntax is some combination of Scheme and Common Lisp. For example, basic function
definition look like:
```
#!scheme
(define (square x)
  (* x x))
```

More complicated functions, however, borrow some syntax from Common Lisp:
```
#!scheme
(define (foo x &optional y)
  (if (null? y)
    x
    y))
```
and
```
#!scheme
(define (foo x &rest rest)
  (if (null? rest)
    x
    rest))
```
For optional arguments, the default is `nil`, someday I'd like to add user-supplies
defaults.

Macros are also of a more Common Lisp flavor.
```
#!scheme
(define-macro (plus x y)
  `(+ ,x ,y))
```
Like Common Lisp, macros are *not* hygeinic, which means variable capture is a problem.
```
#!scheme
>>(define-macro (swap x y)
    `(let ((value ,x))
       (set! ,x ,y)
       (set! ,y ,value)))
swap
>>(define x 1)
x
>>(define value 2)
y
>>(swap value x)
2
>>value
2
>>x
2
```
A basic `gensym` function has been added to help prevent this.
```
#!scheme
>>(define-macro (swap x y)
    (let ((value (gensym)))
      `(let ((,value ,x))
         (set! ,x ,y)
         (set! ,y ,value))))
swap
>>(define x 1)
1
>>(define value 2)
2
>>(swap value x)
2
>>value
1
>>x
2
```

## What Works? ##
# Tail Call Optimization #
Quite a bit works out of the box. The main eval loop is done in a way that we get some
tail-call optimization, thus we can do things like
```
#!scheme
>>(define (fib-iter n a b)
    (if (= n 0)
      a
      (fib-iter (- n 1) b (+ a b))))
fib-iter
>>(define (fib n)
    (fib-iter n 0 1))
fib
>>(fib 10000)
3364476...6875
```
without smashing Python's stack. The downside to the implementation is that it's pretty slow,
even moreso that it's being implemented in a high-level language like Python.

# Macros #
As mentioned above, Lisp Simulacrum has basic macro functionality.
```
#!scheme
>>(define-macro (plus coll)
    `(+ ,@coll))
plus
>>(plus (1 2 3))
6
```

# A Good Amount of Builtins #
`builtins.py` has premade definitions for several useful functions, e.g. `c*r` of
length 3, `length` function for lists, `list-ref`, `map`, and `reduce`.

## Want to know more about Lisp? ##
That's great! Here are some wonderful places to start, in no particular order.

[SICP](https://mitpress.mit.edu/sicp/full-text/book/book.html)

[On Lisp](http://www.paulgraham.com/onlisp.html)

[Practical Common Lisp](http://www.gigamonkeys.com/book/)

[Let Over Lambda](http://letoverlambda.com/)

[Land of Lisp](http://landoflisp.com/)

## Want to know more about language implementation? ##
There are a ton of books out there, and everyone seems to like precisely one and hate all the rest.
My path was to read [SICP](https://mitpress.mit.edu/sicp/full-text/book/book.html) up through
chapter 4 (metalinguistic abstraction) where they build a Lisp in Scheme. Then I picked up a
copy of [Dragon Book](http://dragonbook.stanford.edu/) and read up to somewhere in Chapter 6.
Some other books I've had recommended to me are

[Modern Compiler Implementation in C](http://www.cs.princeton.edu/~appel/modern/c/)

[Language Implementation Patterns](http://pragprog.com/book/tpdsl/language-implementation-patterns)

[Programming Language Pragmatics](https://www.cs.rochester.edu/~scott/pragmatics/)

And, while not a books, I whole heartedly recommend reading Peter Norvig's articles

[(How to Write a (Lisp) Interpreter (in Python))](http://norvig.com/lispy.html)

[(An ((Even Better) Lisp) Interpreter (in Python))](http://norvig.com/lispy2.html)

As well as

[pylisp](https://www.biostat.wisc.edu/~annis/creations/PyLisp/)

[psyche](http://yduppen.home.xs4all.nl/)

[pyscheme](https://hkn.eecs.berkeley.edu/~dyoo/python/pyscheme/)


And if you're interested in some lower level Schemes

[Scheme 9 from Empty Space](http://www.t3x.org/s9fes/)
[TinyScheme](http://tinyscheme.sourceforge.net/)
