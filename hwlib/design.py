#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.exceptions import ParseException
from hwlib.basics import Voltage

__all__ = ["Design"]

NM = 1e-9

PREFIXES = {
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3
}

LIBRARIES = {
    "45nm_HP": {
        "min_feat_size": 45 * NM,
        "includes": ['ptm/45nm_HP.pm']
    }
}


class Net:

    def __init__(self, id):
        self.terminals = set()
        self.id = id

    def connect(self, term):
        self.terminals.add(term)
        term.net = self

    def mergeIn(self, other):
        self.terminals.update(other.terminals)
        for term in other.terminals:
            term.net = self

    def isdisconnected(self):
        return len(self.terminals) == 1

    def get_name(self):
        if isinstance(self.id, str):
            return self.id
        return "net%s" % self.id


class Circuit:

    def __init__(self, parent):
        self.components = set()
        self.id_counter = 0
        self.parent = parent

    def hassubckt(self, subckt):
        return self.parent.hassubckt(subckt)

    def get_id(self):
        self.id_counter += 1
        return self.id_counter

    def add_component(self, component):
        self.components.add(component)
        self.add_header(component.header)

    def add_header(self, h):
        self.parent.add_header(h)

    def disconnect(self, term):
        if term.net is not None:
            if term.net.isdisconnected():
                return
            term.net.remove(term)
        term.net = Net(self.get_id())

    def connect(self, termA, termB):
        if termA.net is None and termB.net is None:
            net = Net(self.get_id())
            net.connect(termA)
            net.connect(termB)
        elif termA.net is None and termB.net is not None:
            termB.net.connect(termA)
        elif termB.net is None and termA.net is not None:
            termA.net.connect(termA)
        else:
            termA.net.mergeIn(termB.net)

    def length(self, length_str):
        return self.parent.length(length_str)

    def print_components(self, stream):
        for c in self.components:
            c.print_netlist(stream)

    def print_netlist(self, stream):
        self.print_components(stream)

    def __getattr__(self, key):
        if self.parent is None:
            raise AttributeError("Circuit has no attribute: %s" % key)
        if key in self.parent.__dict__:
            return self.parent.__dict__[key]
        else:
            raise AttributeError("Circuit has no attribute: %s" % key)


class Design(Circuit):

    def __init__(self, process_library="45nm_HP"):
        Circuit.__init__(self, None)
        self.headers = set()
        self.subckts = dict()

        self.vpwr = Voltage(self, 1.0)
        self.vdd = self.vpwr.plus
        self.vss = self.vpwr.minus

        self.disconnect(self.vdd)
        self.vdd.net.id = "vdd"
        self.disconnect(self.vss)
        self.vss.net.id = "vss"

        for (k, v) in LIBRARIES[process_library].items():
            self.__dict__[k] = v

    def hassubckt(self, subckt):
        return subckt in self.subckts

    def add_subckt(self, subckt):
        assert subckt.id not in self.subckts
        self.subckts[subckt.id] = subckt

    def add_header(self, h):
        self.headers.add(h)

    def length(self, length_str):
        if len(length_str) < 2:
            raise ParseException("length_str is too short")
        if length_str[-1] == 'm':
            factor = length_str[-2]
            if not factor.isalpha():
                return float(length_str[0:-1])
            num = float(length_str[0:-2])
            return num * PREFIXES[factor]

        if length_str[-1] == "X" or length_str[-1] == 'x':
            return float(length_str[0:-1]) * self.min_feat_size

        raise ParseException("Did not recognize length string format")

    def print_includes(self, stream):
        stream.write("*  -- Includes --\n")
        for i in self.includes:
            stream.write(".include %s\n" % i)
        stream.write("\n")

    def print_headers(self, stream):
        stream.write("*  -- Headers --\n")
        for h in self.headers:
            if h != "":
                stream.write(h)
                stream.write("\n")
        stream.write("\n")

        for sc in self.subckts.values():
            sc.print_netlist(stream)
        stream.write("\n")

    def print_components(self, stream):
        stream.write("*  -- Components --\n")
        for c in self.components:
            c.print_netlist(stream)
        stream.write("\n")

    def print_netlist(self, stream):
        self.print_includes(stream)
        self.print_headers(stream)
        self.print_components(stream)
