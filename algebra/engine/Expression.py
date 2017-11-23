# -*- coding: utf-8 -*-

import random
import re as reg
from abc import ABCMeta

from sympy import symbols, sympify, degree, S



class ExpressionError(Exception):
    pass


# ============================================================================
# ================================ Expression ================================
# ============================================================================

class Expression(object):
    """
    This class is the root point of the Algebra engine. As such, it defines a
    set of operations, properties and methods inherents to any kind of
    expression (equation, inequation, equation systems, etc.).

    This class is defined as abstract and as such cannot be instanciated. its
    main purpose is to be subclassed by real expressions ; although static
    methods such as ´generate´ and ´register´ are accessible statically for
    ease of use.

    :see: Equation
    :see: Inequation
    :see: EquationSystem
    """

    __metaclass__ = ABCMeta
    __children__ = set()

    # ---------------------------------------------------------- Magic methods

    def __init__(self, expression, operator=None, domain=S.Reals):
        """
        Class  constructor.

        Analyze the given expression string and computes the result(s) and
        places it in ´self.solution´ or raise and ´ExpressionError´ on syntax
        parsing failure.

        This constructor is not usable by itself as the Expression class is
        abstract. The intended use case is for children subclassing.

        e.g Equation :

            __init__(self, expression, domain):
                Expression.__init__(self, '=', domain)

        The expression is checked and sanitized internally. It is thus not
        necessary to treat the given string beyond standard expression syntax.

        :param expression:  str     The expression string
        :param operator:    str     The expression equality/inequality
                                    comparator, taken from the expression
                                    string if not present.
        :param domain:      sympy.S The domain of the solution, reals by
                                    default.
        """
        self._symbols = [symbols(sym) for sym in self._symbols_of(expression)]
        self._domain = domain

        lo, self._operator, ro = self._split(expression, operator)
        lo = self._sanitize(lo)
        ro = self._sanitize(ro)
        try:
            lcs = {}
            for sym in self._symbols: lcs[str(sym)] = sym
            self._left_operand = sympify(lo, locals=lcs)
            self._right_operand = sympify(ro, locals=lcs)
        except Exception as e:
            raise ExpressionError('Invalid expression syntax, expression: ' +
                                  expression + "\nLeft operand: " + lo +
                                  "\nRIght operand: " + ro)

        lod = degree(self._left_operand)  if self._has_symbol(lo) else 0
        rod = degree(self._right_operand) if self._has_symbol(ro) else 0
        self._degree = lod if lod > rod else rod

        self._solution = self.resolve()

    def __str__(self):
        return self.pretty(
            str(self._left_operand).strip(' ') + ' ' +
            self._operator + ' ' +
            str(self._right_operand).strip(' ')
        )

    def __eq__(self, other):
        return self.solution == other.solution

    # --------------------------------------------------------- Static methods

    @staticmethod
    def register(cls):
        """
        Register the given class as a child of the expression class.
        Only registered classes are generated by the ´generate´ method. The
        children class MUST override the ´generate´ method.

        :param cls: type The Expression inherited class
        """
        Expression.__children__.add(cls)
        return cls

    @staticmethod
    def generate(two_sided, degree):
        """
        Generate an expression which type is taken at random from the
        registered classes.

        :param two_sided:   bool    Whether the expression presents content
                                    at the two sides of the expression or not.
        :param degree:      int     The degree of the expression
        """
        r = random.randint(0, len(Expression.__children__))
        return Expression.__children__[r].generate(two_sided, degree)

    @staticmethod
    def _symbols_of(expression):
        symbol = reg.compile('[a-zA-Z]')
        return set([c.group() for c in symbol.finditer(expression)])

    @staticmethod
    def _sanitize(expression):
        e = expression.replace(' ', '') 
        e = e.replace('+-', '-')
        e = e.replace('-+', '-')
        e = e.replace('--', '+')
        e = e.replace('++', '+')

        sym = reg.compile('[a-zA-Z(]')
        op = reg.compile('[-+*^/%=)(]') # add operators here
        targets = []
        start = lambda r: r.start() == 0
        end = lambda r, expr: r.start() == len(expr) -1
        for c in sym.finditer(e):
            if (start(c) or op.match(e[c.start() - 1])) \
            and (end(c, e) or op.match(e[c.start() + 1])):
                continue

            if not start(c) and not op.match(e[c.start() - 1]):
                targets.append(c.start() - 1)

            if not end(c, e) and not op.match(e[c.start() + 1]):
                if not c.group() == "(":
                    targets.append(c.start() + 1)
        for i, target in enumerate(targets):
            e = e[0:target + 1] + '*' + e[target + 1:len(e)]
            targets[i+1:] = map(lambda x: x + 1, targets[i+1:])
        return e

    @staticmethod
    def _has_symbol(expression):
        s = reg.compile('[a-zA-Z]')
        return s.search(expression) != None

    @staticmethod
    def pretty(expression):
        expr = expression.replace('**', '^')
        expr = expr.replace('*', '')
        return expr.strip(' ')

    @staticmethod
    def _split(expression, operator=None):
        operator = '(<=)|(=<)|(>=)|(=>)|=|<|>' if operator is None else operator
        op_reg = reg.compile(operator)

        op = op_reg.search(expression)
        if not op:
            raise ExpressionError("Unable to split expression: " + expression)
        left, right = expression.split(op.group())

        return left, op.group(), right

    # --------------------------------------------------------- Actual methods

    def resolve(self):
        """
        Find the solution(s) of the expression.

        :return: list<list<str>>
        """
        raise NotImplementedError("Call to abstract method")

    # ------------------------------------------------------------- Properties

    @property
    def solution(self):
        """ The expression solution(s) """
        return self._solution

    @property
    def operator(self):
        """ The expression operator """
        return self._operator

    @property
    def degree(self):
        """ The expression degree """
        return int(self._degree)

    @property
    def symbols(self):
        """ The expression unknown(s) """
        return self._symbols

    @property
    def domain(self):
        """ The expression solution domain """
        return self._domain

    @domain.setter
    def domain(self, dom):
        """ Sets the expression solution domain """
        self._domain = dom

# ============================================================================
