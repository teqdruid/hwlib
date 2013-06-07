#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["Component"]

from string import Formatter
import util
from hwlib.exceptions import UnconnectedException


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
        self.design = design
        design.add_component(self)

    def add_assertions(self):
        pass

    def alter(self, param):
        sid = self.get_spice_id()
        self.design.sim.alter(sid, param)

    def get_spice_line(self):
        f = NetlistFormatter()
        d = dict(self.__dict__)
        d["connections"] = " ".join(map(self.get_connection_str,
                                        self.connection_names))
        for cn in self.connection_names:
            d[cn] = self.get_connection_str(cn)
        return f.vformat(self.netlist_format, [], d)

    def get_spice_id(self):
        return self.get_spice_line().split(" ")[0]

    def get_connection_str(self, cname):
        c = self.__dict__[cname]
        if isinstance(c, str):
            return c
        if c is None or c.net is None:
            raise UnconnectedException(self, cname)
        return c.net.get_name()

    def print_netlist(self, stream):
        s = self.get_spice_line()
        stream.write(s)
        if s[-1] != "\n":
            stream.write("\n")
