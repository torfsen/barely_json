#!/usr/bin/env python
# encoding: utf-8
# __author__ = 'tusharmakkar08'

import codecs
import re

from pyparsing import *

from barely_json.illegal_value import IllegalValue


def to_float(t):
    '''
    Convert a string that looks like a float to a float.
    '''
    return float(re.sub(r'\s*', '', t[0]))


def to_int(t):
    '''
    Convert a string that looks like an int to an int.
    '''
    return int(re.sub(r'\s*', '', t[0]))


# From http://stackoverflow.com/a/24519338/857390

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    '''
    Decode string escape sequences.
    '''
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')
    result = ESCAPE_SEQUENCE_RE.sub(decode_match, s)
    return result


L_BRACKET, R_BRACKET, L_BRACE, R_BRACE, COLON, COMMA = map(Suppress, '[]{}:,')

integrated_grammar_value = Forward()

null = Keyword('null').setParseAction(lambda: None)

true = Keyword('true').setParseAction(lambda: True)
false = Keyword('false').setParseAction(lambda: False)

int_ = Regex(r'[+-]?\s*\d+').setParseAction(to_int)

FLOAT_RE = r'[+-]?\s*(0(\.\d*)?|([1-9]\d*\.?\d*)|(\.\d+))([Ee][+-]?\d+)?'

float_ = Regex(FLOAT_RE).setParseAction(to_float)

# PyParsing's QuotedString preprocesses some escape sequences incorrectly,
# so we're doing things manually.
string_ = Regex(r'".*?(?<!\\)(\\\\)*"')\
            .setParseAction(lambda t: decode_escapes(t[0][1:-1]))

empty = Empty().setParseAction(lambda: IllegalValue(''))

# Special case the empty list to avoid [IllegalValue('')]
list_ = (
    (L_BRACKET + R_BRACKET).setParseAction(lambda: [[]]) |
    Group(L_BRACKET + Optional(delimitedList(integrated_grammar_value ^ empty)) + R_BRACKET)
)

illegal = Combine(OneOrMore(quotedString ^ Regex(r'[^,{}[\]]')))\
                .setParseAction(lambda t: IllegalValue(t[0].strip()))
# Like ``illegal`` but doesn't allow colons
illegal_key = Combine(OneOrMore(quotedString ^ Regex(r'[^:,{}[\]]')))\
                .setParseAction(lambda t: IllegalValue(t[0].strip()))

dict_key = string_ | illegal_key
dict_value = Optional(integrated_grammar_value, default=IllegalValue(''))
dict_item = Group(dict_key + Optional(COLON + dict_value,
                  default=IllegalValue('')))
dict_content = delimitedList(dict_item ^ Empty())\
                .setParseAction(lambda t: dict(t.asList()))
dict_ = L_BRACE + dict_content + R_BRACE

integrated_grammar_value << (dict_ | list_ | float_ | int_ | string_ |
                             null | true | false | illegal)
