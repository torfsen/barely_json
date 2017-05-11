#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import math
from itertools import izip

from barely_json import *


empty = EmptyValue()


def pairwise(iterable):
    '''
    s -> (s0, s1), (s2, s3), (s4, s5), ...
    '''
    a = iter(iterable)
    return izip(a, a)


class TestParse(object):

    def check(self, *args, **kwargs):
        resolver = kwargs.pop('resolver', None)
        for code, expected in pairwise(args):
            assert parse(code, resolver=resolver) == expected

    def test_empty_list(self):
        self.check(
            '[]', [],
            '[ ]', [],
            '[\n]', [],
            '[\t]', [],
        )

    def test_empty_list_element(self):
        self.check(
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

    def test_empty_dict(self):
        self.check(
            '{}', {},
            '{ }', {},
            '{\n}', {},
            '{\t}', {},
        )

    def test_dict(self):
        self.check(
            '{1: 2}', {SpecialValue('1'): 2},
            '{1: 2, 3: 4}', {SpecialValue('1'): 2, SpecialValue('3'): 4},
            "{'1': 2}", {SpecialValue("'1'"): 2},
            '{"1": 2}', {'1': 2},
            '''{a b ":" ':' 2 3 : 1}''', {SpecialValue('''a b ":" ':' 2 3'''): 1},
        )

    def test_empty_dict_element(self):
        self.check(
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

    def test_missing_dict_value(self):
        self.check(
            '{"a"}', {'a': EmptyValue()},
            '{"a", "b": 1}', {'a': EmptyValue(), 'b': 1},
            '{"a": 1, "b"}', {'a': 1, 'b': EmptyValue()},
            '{"a":}', {'a': EmptyValue()},
            '{"a":, "b": 1}', {'a': EmptyValue(), 'b': 1},
            '{"a": 1, "b":}', {'a': 1, 'b': EmptyValue()},
        )


class TestDefaultResolver(object):

    def check(self, *args):
        for value, expected in pairwise(args):
            assert default_resolver(value) == expected

    def test_empty(self):
        self.check(None, None)

    def test_boolean(self):
        self.check(
            'TRUE', True,
            'true', True,
            'YES', True,
            'yes', True,
            'ON', True,
            'on', True,
            'FALSE', False,
            'false', False,
            'NO', False,
            'no', False,
            'OFF', False,
            'off', False,
        )

    def test_null(self):
        self.check(
            'NULL', None,
            'null', None,
            'NONE', None,
            'none', None,
        )

    def test_float(self):
        self.check(
            'INF', float('inf'),
            'inf', float('inf'),
            '-INF', float('-inf'),
            '-inf', float('-inf'),
            '0', 0,
            '1', 1,
            '-1', -1,
            '0.04', 0.04,
            '-21.432', -21.432,
            '2.4e-3', 2.4e-3,
            '-34.12E9', -34.12e9,
        )
        for value in ['nan', 'NaN', 'NAN']:
            assert math.isnan(default_resolver(value))

    def test_unknown(self):
        self.check(
            'foo', 'foo',
            'FOO', 'FOO',
        )


class TestResolve(object):

    def check(self, *args, **kwargs):
        resolver = kwargs.pop('resolver', default_resolver)
        for value, expected in pairwise(args):
            assert resolve(value, resolver=resolver) == expected

    def test_list(self):
        self.check(
            [], [],
            [1, 'foo', True], [1, 'foo', True],
            [empty, SpecialValue('NO')], [None, False],
        )

    def test_dict(self):
        self.check(
            {}, {},
            {'a': 1, 'b': True, 'c': None}, {'a': 1, 'b': True, 'c': None},
            {'a': empty}, {'a': None},
            {'a': SpecialValue('false')}, {'a': False},
            {SpecialValue('YES'): SpecialValue('no')}, {True: False},
        )

    def test_scalar(self):
        self.check(
            1, 1,
            'foo', 'foo',
            empty, None,
            SpecialValue('YES'), True,
        )

    def test_nested(self):
        self.check(
            [empty, {SpecialValue('yes'): [SpecialValue('no')]}],
            [None, {True: [False]}]
        )

    def test_custom_resolver(self):
        resolver = lambda value: 1 if value == 'one' else value
        self.check(
            SpecialValue('one'), 1,
            SpecialValue('true'), 'true',
            [SpecialValue('one')], [1],
            [SpecialValue('true')], ['true'],
            {SpecialValue('one'): SpecialValue('one')}, {1: 1},
            {SpecialValue('true'): SpecialValue('true')}, {'true': 'true'},
            resolver=resolver
        )

