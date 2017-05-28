#!/usr/bin/env python
# encoding: utf-8

'''
A very forgiving JSON parser.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

from six import iteritems

from barely_json.illegal_value import IllegalValue
from barely_json.grammar import decode_escapes, integrated_grammar_value

__version__ = '0.1.1'


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
        return {resolve(key, resolver): resolve(value, resolver) for key, value in iteritems(data)}
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
    parsed = integrated_grammar_value.parseString(s, parseAll=True)
    data = parsed.asList()[0]
    if resolver:
        data = resolve(data, resolver=resolver)
    return data
