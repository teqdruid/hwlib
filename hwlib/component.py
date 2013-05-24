#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["Component"]

from string import Formatter
import util


class NetlistFormatter(Formatter):

    def format_field(self, value, format_spec):
        if format_spec == "len":
            return util.readable_length(value)
        return format(value, format_spec)


class Component:

    header = ""
    netlist_format = ""

    def __init__(self, design, connections):
        self._connection_names = connections
        self.id = design.get_id()
        design.add_component(self)

    def print_netlist(self, stream):
        f = NetlistFormatter()
        d = dict(self.__dict__)
        d["connections"] = ""
        s = f.vformat(self.netlist_format, [], d)
        stream.write(s)
        if s[-1] != "\n":
            stream.write("\n")
