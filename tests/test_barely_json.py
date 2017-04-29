#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from itertools import izip

import barely_json


def pairwise(iterable):
    '''
    s -> (s0, s1), (s2, s3), (s4, s5), ...
    '''
    a = iter(iterable)
    return izip(a, a)


def check(*args):
    for code, expected in pairwise(args):
        assert barely_json.parse(code) == expected


def test_empty_list():
    check(
        '[]', [],
        '[ ]', [],
        '[\n]', [],
        '[\t]', [],
    )

