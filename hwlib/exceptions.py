#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ParseException(BaseException):

    def __init__(self, msg):
        BaseException.__init__(msg)
