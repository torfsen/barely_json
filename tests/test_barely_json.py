#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from itertools import izip

from barely_json import *


empty = EmptyValue()


def pairwise(iterable):
    '''
    s -> (s0, s1), (s2, s3), (s4, s5), ...
    '''
    a = iter(iterable)
    return izip(a, a)


def check(*args):
    for code, expected in pairwise(args):
        #print(barely_json.parse(code))
        assert parse(code) == expected


def test_empty_list():
    check(
        '[]', [],
        '[ ]', [],
        '[\n]', [],
        '[\t]', [],
    )


def test_empty_list_element():
    check(
        '[,]', [empty, empty],
        '[,,]', [empty, empty, empty],
        '[1,]', [1, empty],
        '[1,,]', [1, empty, empty],
        '[,1]', [empty, 1],
        '[,,1]', [empty, empty, 1],
        '[1,,2]', [1, empty, 2],
        '[1,,2,]', [1, empty, 2, empty],
        '[1,,,2]', [1, empty, empty, 2],
    )


def test_empty_dict():
    check(
        '{}', {},
        '{ }', {},
        '{\n}', {},
        '{\t}', {},
    )


def test_dict():
    check(
        '{1: 2}', {SpecialValue('1'): 2},
        '{1: 2, 3: 4}', {SpecialValue('1'): 2, SpecialValue('3'): 4},
        "{'1': 2}", {SpecialValue("'1'"): 2},
        '{"1": 2}', {'1': 2},
        '''{a b ":" ':' 2 3 : 1}''', {SpecialValue('''a b ":" ':' 2 3'''): 1},
    )


def test_empty_dict_element():
    check(
        '{,}', {},
        '{,,}', {},
        '{,,,}', {},
        '{"a":1,}', {'a': 1},
        '{"a":1,,}', {'a': 1},
        '{,,"a":1}', {'a': 1},
        '{,"a":1,}', {'a': 1},
        '{"a":1,,"b":2}', {'a': 1, 'b': 2},
        '{"a":1,,,"b":2}', {'a': 1, 'b': 2},
    )


def test_missing_dict_value():
    check(
        '{"a"}', {'a': EmptyValue()},
        '{"a", "b": 1}', {'a': EmptyValue(), 'b': 1},
        '{"a": 1, "b"}', {'a': 1, 'b': EmptyValue()},
        '{"a":}', {'a': EmptyValue()},
        '{"a":, "b": 1}', {'a': EmptyValue(), 'b': 1},
        '{"a": 1, "b":}', {'a': 1, 'b': EmptyValue()},
    )
