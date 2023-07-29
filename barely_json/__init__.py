#!/usr/bin/env python

'''
A very forgiving JSON parser.
'''

import codecs
import re

from pyparsing import *


__version__ = '1.0.0'


class IllegalValue:
    '''
    A value that is illegal in JSON.

    ``parse`` wraps anything that isn't standard JSON into an
    ``IllegalValue`` instance. By default, these are then automatically
    resolved into standard Python types via ``resolve``. However, if you
    pass ``resolver=None`` to ``parse`` and your input contains illegal
    values then your output will contain instances of this class.

    The part of the source that is represented by this instance is
    stored in the ``source`` attribute. That may be the empty string in
    cases like ``[1, , 2]``.
    '''
    def __init__(self, source):
        '''
        Constructor.

        ``source`` is a string.
        '''
        self.source = source

    def __str__(self):
        return self.source

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.source)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.source == self.source)

    def __hash__(self):
        return hash(self.source)


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

value = Forward()

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
    Group(L_BRACKET + Optional(delimitedList(value ^ empty)) + R_BRACKET)
)

illegal = Combine(OneOrMore(quotedString ^ Regex(r'[^,{}[\]]')))\
                .setParseAction(lambda t: IllegalValue(t[0].strip()))
# Like ``illegal`` but doesn't allow colons
illegal_key = Combine(OneOrMore(quotedString ^ Regex(r'[^:,{}[\]]')))\
                .setParseAction(lambda t: IllegalValue(t[0].strip()))

dict_key = string_ | illegal_key
dict_value = Optional(value, default=IllegalValue(''))
dict_item = Group(dict_key + Optional(COLON + dict_value,
                  default=IllegalValue('')))
dict_content = delimitedList(dict_item ^ Empty())\
                .setParseAction(lambda t: dict(t.asList()))
dict_ = L_BRACE + dict_content + R_BRACE

value << (dict_ | list_ | float_ | int_ | string_ |
          null | true | false | illegal)


def default_resolver(value):
    '''
    Default resolver for illegal values.

    Case-insensitively resolves

    - ``'true'``, ``'yes'``, and ``'on'`` to ``True``

    - ``'false'``, ``'no'``, and ``'off'`` to ``False``

    - ``'null'`` and ``'none'`` to ``None``

    - ``'inf'``, ``'-inf'``, and ``'nan'`` to their ``float``
      counterparts

    All other strings are returned unchanged.
    '''
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
    return decode_escapes(value)


def resolve(data, resolver=default_resolver):
    '''
    Recursively resolve illegal values.

    ``data`` is a potentially nested Python value as returned by
    ``parse``.

    ``resolver`` is a function that maps strings to arbitrary values.

    All instances of ``IllegalValue`` in ``data`` are replaced by the
    result of feeding them into ``resolver``.
    '''
    if isinstance(data, list):
        return [resolve(item, resolver) for item in data]
    if isinstance(data, dict):
        return {resolve(key, resolver): resolve(value, resolver) for key, value in data.items()}
    if isinstance(data, IllegalValue):
        return resolver(data.source)
    return data


def parse(s, resolver=default_resolver):
    '''
    Parse a string that contains barely JSON.

    When values that are illegal in JSON are encountered then they are
    by default heuristicaly resolved to a suitable Python type (see
    ``resolve`` and ``default_resolver``). Set ``resolver`` to a custom
    callback or to a falsy value to modify or disable that mechanism.
    '''
    parsed = value.parseString(s, parseAll=True)
    data = parsed.asList()[0]
    if resolver:
        data = resolve(data, resolver=resolver)
    return data
