#!/usr/bin/env python
# -*- coding: utf-8 -*-

PREFIXES = {
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3
}


def readable_length(meters):
    if meters >= 1:
        return "%sm" % (meters)
    if meters >= 1e-3:
        return "%smm" % (meters * 1e3)
    if meters >= 1e-6:
        return "%sum" % (meters * 1e6)
    if meters >= 1e-9:
        return "%snm" % (meters * 1e9)
    return "%sm" % (meters)


def parse_suffix(num):
    factor = num[-1]
    if not factor.isalpha():
        return float(num)
    num = float(num[0:-1])
    return num * PREFIXES[factor]
