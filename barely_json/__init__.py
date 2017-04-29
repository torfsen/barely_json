#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ast
import re

from pyparsing import *


__version__ = '0.1.0'


# Based on http://stackoverflow.com/a/3602436/857390

class SpecialValue(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return text

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.text)

    def resolve(self):
        low = self.text.lower()
        no_space = re.sub(r'\s+', '', low)
        if low in ['true', 'yes', 'on']:
            return True
        if low in ['false', 'no', 'off']:
            return False
        if low in ['null', 'none']:
            return None
        try:
            # Handles +/- NaN/Inf
            return float(no_space)
        except ValueError:
            pass
        try:
            return ast.literal_eval(self.text)
        except ValueError:
            pass
        return self


class EmptyValue(SpecialValue):
    def __init__(self):
        super(EmptyValue, self).__init__('')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


#def CaselessKeywords(*args):
#    return Or(map(CaselessKeyword, args))


def _to_float(t):
    return float(re.sub(r'\s*', '', t[0]))


# Idea: Parse anything that's not strict JSON into a SpecialValue. Resolve
# common special values (e.g. "nan") into sensible Python values by default
# but let the user disable that to do their own conversion.


L_BRACKET, R_BRACKET, L_BRACE, R_BRACE, COLON, COMMA = map(Suppress, '[]{}:,')

value = Forward()

null = Keyword('null').setParseAction(lambda: None)

true = Keyword('true').setParseAction(lambda: True)
false = Keyword('false').setParseAction(lambda: False)

int_ = Regex(r'[+-]?\s*\d+').setParseAction(lambda t: int(t[0]))

FLOAT_RE = r'[+-]?\s*(0(\.\d*)?|([1-9]\d*\.?\d*)|(\.\d+))([Ee][+-]?\d+)?'
float_ = Regex(FLOAT_RE).setParseAction(_to_float)

string_ = QuotedString('"')

list_ = Group(L_BRACKET +
             Optional(delimitedList(value ^
                                    Empty().setParseAction(lambda: EmptyValue()))) +
             R_BRACKET)

key = Combine(ZeroOrMore(quotedString ^ Regex(r'[^:]')))
dict_ = Group(L_BRACE +
              Optional(dictOf(key + COLON, value + Optional(COMMA))) +
              R_BRACE)

special = Combine(OneOrMore(quotedString ^ Regex(r'[^,{}[\]]'))).setParseAction(lambda t: SpecialValue(t[0]))

value << (dict_ | list_ | int_ | float_ | string_ | null | true | false | special)




def parse(s):
    return value.parseString(s, parseAll=True)


