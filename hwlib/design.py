#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hwlib.component import Component
from hwlib.exceptions import ParseException, BadConnectionException
from hwlib.basics import Voltage
import util

__all__ = ["Design"]

NM = 1e-9

LIBRARIES = {
    "45nm_LP": {
        "min_feat_size": 45 * NM,
        "min_gate_width": 160 * NM,
        "nominal_vdd": 1.1,
        "pn_ratio": 1.484375,
        "includes": ['ptm/45nm_LP.pm']
    },
    "45nm_HP": {
        "min_feat_size": 45 * NM,
        "min_gate_width": 160 * NM,
        "nominal_vdd": 1.0,
        "pn_ratio": 2.5078,
        "includes": ['ptm/45nm_HP.pm']
    },
    "32nm_LP": {
        "min_feat_size": 32 * NM,
        "min_gate_width": 120 * NM,
        "nominal_vdd": 1.0,
        "pn_ratio": 1.40625,
        "includes": ['ptm/32nm_LP.pm']
    },
    "32nm_HP": {
        "min_feat_size": 32 * NM,
        "min_gate_width": 120 * NM,
        "nominal_vdd": 0.9,
        "pn_ratio": 2.1484375,
        "includes": ['ptm/32nm_HP.pm'],
        "M1Pitch": 110e-9,
        "M1ResPerM": 4e6,
        "M1IndPerM": 1.53e6,
        "M1CoupCapPerM": 15.521e-12,
        "M1GndCapPerM": 2*203.567e-12,
#         "M1ResPerM": 0,
#         "M1IndPerM": 0,
#         "M1CoupCapPerM": 0,
#         "M1GndCapPerM": 0,
    },
    "22nm_LP": {
        "min_feat_size": 25 * NM,
        "min_gate_width": 100 * NM,
        "nominal_vdd": 0.95,
        "pn_ratio": 1.479,
        "includes": ['ptm/22nm_LP.pm']
    },
    "22nm_HP": {
        "min_feat_size": 25 * NM,
        "min_gate_width": 100 * NM,
        "nominal_vdd": 0.8,
        "pn_ratio": 1.66406,
        "includes": ['ptm/22nm_HP.pm']
    },
    "16nm_LP": {
        "min_feat_size": 16 * NM,
        "min_gate_width": 80 * NM,
        "nominal_vdd": 0.9,
        "pn_ratio": 2.640625,
        "includes": ['ptm/16nm_LP.pm']
    },
    "16nm_HP": {
        "min_feat_size": 16 * NM,
        "min_gate_width": 80 * NM,
        "nominal_vdd": 0.7,
        "pn_ratio": 1.3046875,
        "includes": ['ptm/16nm_HP.pm']
    },
}

import os
MyDir = os.path.dirname(__file__)


class Net:

    def __init__(self, id):
        self.terminals = set()
        self.id = id

    def connect(self, term):
        self.terminals.add(term)
        term.net = self

    def mergeIn(self, other):
        if isinstance(self.id, str) and isinstance(other.id, str) and \
                self.id != other.id:
            raise BadConnectionException(
                "Cannot connent different named nets: %s, %s" %
                (self.id, other.id))
        self.terminals.update(other.terminals)
        for term in other.terminals:
            term.net = self
        if isinstance(other.id, str):
            self.id = other.id

    def isdisconnected(self):
        return len(self.terminals) == 1

    def remove(self, term):
        self.terminals.remove(term)
        term.net = None

    def name(self, name):
        if isinstance(self.id, str) and isinstance(name, str) and \
                self.id != name:
            raise BadConnectionException(
                "Cannot rename net '%s' to '%s'!" % (self.id, name))
        self.id = name

    def get_name(self):
        if isinstance(self.id, str):
            return self.id
        return "net%s" % self.id


class Circuit:

    def __init__(self, parent):
        self.components = []
        self.net_names = set()
        self.id_counter = 0
        self.parent = parent

    def hassubckt(self, subckt):
        return self.parent.hassubckt(subckt)

    def get_id(self):
        self.id_counter += 1
        return self.id_counter

    def add_component(self, component):
        self.components.append(component)
        self.add_header(component.header)

    def add_header(self, h):
        self.parent.add_header(h)

    def disconnect(self, term):
        if term.net is not None:
            if term.net.isdisconnected():
                return
            term.net.remove(term)

    def allow_disconnect(self, term):
        if term.net is None:
            term.net = Net(self.get_id())

    def connect(self, termA, termB):
        if isinstance(termB, str):
            if termA.net is None:
                termA.net = Net(termB)
            else:
                termA.net.name(termB)
        elif termA.net is None and termB.net is None:
            net = Net(self.get_id())
            net.connect(termA)
            net.connect(termB)
        elif termA.net is None and termB.net is not None:
            termB.net.connect(termA)
        elif termB.net is None and termA.net is not None:
            termA.net.connect(termB)
        else:
            termA.net.mergeIn(termB.net)

    def name(self, names):
        for (term, name) in names.items():
            net = term
            if isinstance(term, Component):
                assert name not in self.net_names
                self.net_names.add(name)
                term.id = name
            else:
                if not isinstance(term, Net):
                    if term.net is None:
                        term.net = Net(self.get_id())
                    net = term.net
                assert name not in self.net_names
                net.name(name)

    def pair(self, pairs):
        for (a, b) in pairs.items():
            self.connect(a, b)

    def length(self, length_str):
        return self.parent.length(length_str)

    def add_assertions(self):
        for c in self.components:
            c.add_assertions()

    def print_components(self, stream):
        for c in self.components:
            c.print_netlist(stream)

    def print_netlist(self, stream):
        self.print_components(stream)

    def write_netlist(self, fn):
        f = file(fn, "w")
        self.print_netlist(f)
        f.close

    def __getattr__(self, key):
        if self.parent is None:
            raise AttributeError("Circuit has no attribute: %s" % key)
        if hasattr(self.parent, key):
            return getattr(self.parent, key)
        else:
            raise AttributeError("Circuit has no attribute: %s" % key)


class Design(Circuit):

    def __init__(self, vdd_voltage=None, process_library="45nm_HP"):
        Circuit.__init__(self, None)
        self.headers = set()
        self.subckts = dict()
        self.process_library = process_library

        for (k, v) in LIBRARIES[process_library].items():
            self.__dict__[k] = v

        if vdd_voltage is None:
            vdd_voltage = self.nominal_vdd

        self.vss = Component.Terminal(self)

        self.vpwr = Voltage(self, vdd_voltage)
        self.name({self.vpwr: "vdd"})
        self.vdd = self.vpwr.plus

        self.allow_disconnect(self.vdd)
        self.vdd.net.id = "vdd"
        self.allow_disconnect(self.vss)
        self.vss.net.id = "0"

        self.init_conds = []

        # NGSpice likes a zero reference
        # vss = Voltage(self, 0.0)
        # vss.minus = "0"
        # self.name({vss: "0"})
        # self.connect(self.vss, vss.plus)

    def hassubckt(self, subckt):
        return subckt in self.subckts

    def add_subckt(self, subckt):
        assert subckt.id not in self.subckts
        self.subckts[subckt.id] = subckt

    def set_simulation(self, sim):
        self.sim = sim

    def set_initial_condition(self, net, v):
        self.init_conds.append((net, v))

    def add_header(self, h):
        self.headers.add(h)

    def length(self, length_str):
        if isinstance(length_str, float):
            return length_str
        if len(length_str) < 2:
            raise ParseException("length_str is too short")
        if length_str[-1] == 'm':
            return util.parse_suffix(length_str[0:-1])

        if length_str[-1] == "X" or length_str[-1] == 'x':
            return float(length_str[0:-1]) * self.min_feat_size

        raise ParseException("Did not recognize length string format")

    def width(self, length_str):
        if isinstance(length_str, float):
            return length_str
        if len(length_str) < 2:
            raise ParseException("length_str is too short")
        if length_str[-1] == 'm':
            return util.parse_suffix(length_str[0:-1])

        if length_str[-1] == "X" or length_str[-1] == 'x':
            return float(length_str[0:-1]) * self.min_gate_width

        raise ParseException("Did not recognize length string format")

    def add_assertions(self):
        for c in self.components:
            c.add_assertions()

    def print_includes(self, stream):
        stream.write("*  -- Includes --\n")
        for i in self.includes:
            stream.write(".include %s/../%s\n" % (MyDir, i))
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

    def print_netlist(self, stream=sys.stdout):
        self.print_includes(stream)
        self.print_headers(stream)
        self.print_components(stream)
