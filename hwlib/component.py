#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["Component"]

from string import Formatter
import util
from exceptions import UnconnectedException


class NetlistFormatter(Formatter):

    def format_field(self, value, format_spec):
        if format_spec == "len":
            return util.readable_length(value)
        return format(value, format_spec)


class Component:

    class Terminal:

        def __init__(self, component):
            self.owner = component
            self.net = None

    header = ""
    netlist_format = ""
    connection_names = []

    def __init__(self, design):
        for cn in self.connection_names:
            self.__dict__[cn] = Component.Terminal(self)
        self.id = design.get_id()
        design.add_component(self)

    def get_connection_str(self, cname):
        c = self.__dict__[cname]
        if isinstance(c, str):
            return c
        if c is None or c.net is None:
            raise UnconnectedException(cname)
        return c.net.get_name()

    def print_netlist(self, stream):
        f = NetlistFormatter()
        d = dict(self.__dict__)
        d["connections"] = " ".join(map(self.get_connection_str,
                                        self.connection_names))
        s = f.vformat(self.netlist_format, [], d)
        stream.write(s)
        if s[-1] != "\n":
            stream.write("\n")
