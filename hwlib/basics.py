#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import Component


class NMos(Component):

    netlist_format = "Mn{id} {connections} nmos l={length:len} w={width:len}"

    def __init__(self, design, width='1x', length='1x'):
        Component.__init__(self, design, ['gate', 'source', 'drain', 'body'])
        self.length = design.length(length)
        self.width = design.length(width)
        # self.body = design.vss


# class PMos(Component):

#     netlist_format = "Mp{id} {connections} pmos l={len:length} w={len:width}"

#     def __init__(self, design, width='2x', length='1x'):
#         Component.__init__(self, design, ['gate', 'source', 'drain', 'body'])
#         self.length = design.length(length)
#         self.width = design.length(width)
#         design.connect(self.body, design.vdd)
