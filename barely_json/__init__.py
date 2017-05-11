#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.text == self.text

    def __hash__(self):
        return hash(self.text)


class EmptyValue(SpecialValue):
    def __init__(self):
        super(EmptyValue, self).__init__(None)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False


#def CaselessKeywords(*args):
#    return Or(map(CaselessKeyword, args))


def to_float(t):
    return float(re.sub(r'\s*', '', t[0]))

def to_int(t):
    return int(re.sub(r'\s*', '', t[0]))


L_BRACKET, R_BRACKET, L_BRACE, R_BRACE, COLON, COMMA = map(Suppress, '[]{}:,')

value = Forward()

null = Keyword('null').setParseAction(lambda: None)

true = Keyword('true').setParseAction(lambda: True)
false = Keyword('false').setParseAction(lambda: False)

int_ = Regex(r'[+-]?\s*\d+').setParseAction(to_int)

FLOAT_RE = r'[+-]?\s*(0(\.\d*)?|([1-9]\d*\.?\d*)|(\.\d+))([Ee][+-]?\d+)?'
float_ = Regex(FLOAT_RE).setParseAction(to_float)

string_ = QuotedString('"')

empty = Empty().setParseAction(lambda: EmptyValue())


# Special case the empty list to avoid EmptyValue
list_ = (
        (L_BRACKET + R_BRACKET).setParseAction(lambda: [[]]) |
        Group(L_BRACKET +
             Optional(delimitedList(value ^
                                    Empty().setParseAction(lambda: EmptyValue()))) +
             R_BRACKET)
        )


special = Combine(OneOrMore(quotedString ^ Regex(r'[^,{}[\]]'))).setParseAction(lambda t: SpecialValue(t[0].strip()))
# Like ``special`` but doesn't allow colons
special_key = Combine(OneOrMore(quotedString ^ Regex(r'[^:,{}[\]]'))).setParseAction(lambda t: SpecialValue(t[0].strip()))

key = string_ | special_key

dict_item = Group(key + Optional(COLON + Optional(value, default=EmptyValue()), default=EmptyValue()))
dict_content = delimitedList(dict_item ^ Empty()).setParseAction(lambda t: dict(t.asList()))
dict_ = L_BRACE + dict_content + R_BRACE


value << (dict_ | list_ | int_ | float_ | string_ | null | true | false | special)


def default_resolver(value):
    if value is None:
        return None
    low = value.lower()
    if low in ['true', 'yes', 'on']:
        return True
    if low in ['false', 'no', 'off']:
        return False
    if low in ['null', 'none']:
        return None
    try:
        # Handles +/- NaN/Inf
        return float(re.sub(r'\s+', '', low))
    except ValueError:
        pass
    return value


def resolve(data, resolver=default_resolver):
    if isinstance(data, list):
        items = []
        for item in data:
            items.append(resolve(item, resolver))
        return items
    if isinstance(data, dict):
        items = {}
        for key, value in data.iteritems():
            items[resolve(key, resolver)] = resolve(value, resolver)
        return items
    if isinstance(data, SpecialValue):
        return resolver(data.text)
    return data


def parse(s, resolver=default_resolver):
    parsed = value.parseString(s, parseAll=True)
    data = parsed.asList()[0]
    if resolver:
        data = resolve(data, resolver=resolver)
    return data

