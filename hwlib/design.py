#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.exceptions import ParseException

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


class Design:

    def __init__(self, process_library="45nm_HP"):
        self.components = set()
        self.id_counter = 0
        self.headers = set()

        for (k, v) in LIBRARIES[process_library].items():
            self.__dict__[k] = v

    def get_id(self):
        self.id_counter += 1
        return self.id_counter

    def add_component(self, component):
        self.components.add(component)
        self.headers.add(component.header)

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

    def print_components(self, stream):
        stream.write("*  -- Components --\n")
        for c in self.components:
            c.print_netlist(stream)
        stream.write("\n")

    def print_netlist(self, stream):
        self.print_includes(stream)
        self.print_headers(stream)
        self.print_components(stream)
