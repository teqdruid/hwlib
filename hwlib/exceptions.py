#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ParseException(BaseException):

    def __init__(self, msg):
        BaseException.__init__(self, msg)


class UnconnectedException(BaseException):

    def __init__(self, dev, term):
        BaseException.__init__(
            self, "Found unconnected terminal '%s' in device '%s'" % (
                term, dev))
