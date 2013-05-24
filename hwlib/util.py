#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
