#!/usr/bin/env python

import math

from barely_json import *

empty = IllegalValue('')

STRING_ESCAPE_TESTS = [
    r'\t', '\t',
    r'\\', '\\',
    r'\\\\', '\\\\',
    r'\\\\\\', '\\\\\\',
    r'\"', '"',
    r'\\\"', '\\"',
    r'\\\\\"', '\\\\"',
    r'\'', "'",
    r'\a', '\a',
    r'\b', '\b',
    r'\f', '\f',
    r'\n', '\n',
    r'\r', '\r',
    r'\t', '\t',
    r'\v', '\v',
    r'\o1', r'\o1',
    r'\o12', r'\o12',
    r'\o123', r'\o123',
    r'\xef', '\xef',
    r'\xEF', '\xef',
    r'\N{SNOWMAN}', '\N{SNOWMAN}',
    r'\u2603', '\u2603',
    r'\U00002603', '\U00002603',
]


def pairwise(iterable):
    '''
    s -> (s0, s1), (s2, s3), (s4, s5), ...
    '''
    a = iter(iterable)
    return zip(a, a)


class TestParse:
    @staticmethod
    def check(*args, **kwargs):
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
            '{1: 2}', {IllegalValue('1'): 2},
            '{1: 2, 3: 4}', {IllegalValue('1'): 2, IllegalValue('3'): 4},
            "{'1': 2}", {IllegalValue("'1'"): 2},
            '{"1": 2}', {'1': 2},
            '''{a b ":" ':' 2 3 : 1}''', {IllegalValue('''a b ":" ':' 2 3'''): 1},
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
            '{"a"}', {'a': empty},
            '{"a", "b": 1}', {'a': empty, 'b': 1},
            '{"a": 1, "b"}', {'a': 1, 'b': empty},
            '{"a":}', {'a': empty},
            '{"a":, "b": 1}', {'a': empty, 'b': 1},
            '{"a": 1, "b":}', {'a': 1, 'b': empty},
        )

    def test_numbers(self):
        self.check(
            '0', 0,
            '-0', 0,
            '+0', 0,
            '1', 1,
            '+1', 1,
            '-1', -1,
            '10', 10,
            '+10', 10,
            '-10', -10,
            '0.123', 0.123,
            '+0.123', 0.123,
            '-0.123', -0.123,
            '.123', .123,
            '+.123', .123,
            '-.123', -.123,
            '1.', 1.0,
            '+1.', 1.0,
            '-1.', -1.0,
            '123.e10', 123e10,
            '-123.E-3', -123e-3,
        )

    def test_string_escapes(self):
        cases = (
            ('"{}"'.format(x), y) for x, y in pairwise(STRING_ESCAPE_TESTS)
        )
        self.check(*(x for case in cases for x in case))


class TestDefaultResolver:
    @staticmethod
    def check(*args):
        for value, expected in pairwise(args):
            assert default_resolver(value) == expected

    def test_empty(self):
        self.check('', '')

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

    def test_string_escapes(self):
        self.check(*STRING_ESCAPE_TESTS)


class TestResolve:
    @staticmethod
    def check(*args, **kwargs):
        resolver = kwargs.pop('resolver', default_resolver)
        for value, expected in pairwise(args):
            assert resolve(value, resolver=resolver) == expected

    def test_list(self):
        self.check(
            [], [],
            [1, 'foo', True], [1, 'foo', True],
            [empty, IllegalValue('NO')], ['', False],
        )

    def test_dict(self):
        self.check(
            {}, {},
            {'a': 1, 'b': True, 'c': None}, {'a': 1, 'b': True, 'c': None},
            {'a': empty}, {'a': ''},
            {'a': IllegalValue('false')}, {'a': False},
            {IllegalValue('YES'): IllegalValue('no')}, {True: False},
        )

    def test_scalar(self):
        self.check(
            1, 1,
            'foo', 'foo',
            empty, '',
            IllegalValue('YES'), True,
        )

    def test_nested(self):
        self.check(
            [empty, {IllegalValue('yes'): [IllegalValue('no')]}],
            ['', {True: [False]}]
        )

    def test_custom_resolver(self):
        def resolver(value):
            if value == 'one':
                return 1
            return value

        self.check(
            IllegalValue('one'), 1,
            IllegalValue('true'), 'true',
            [IllegalValue('one')], [1],
            [IllegalValue('true')], ['true'],
            {IllegalValue('one'): IllegalValue('one')}, {1: 1},
            {IllegalValue('true'): IllegalValue('true')}, {'true': 'true'},
            resolver=resolver
        )


class TestIllegalValue:
    def test_str_illegal(self):
        assert str(IllegalValue('one')) == 'one'
