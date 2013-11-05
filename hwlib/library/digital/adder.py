#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hwlib.component import WArray
from hwlib.subcircuit import SubcktComponent
from hwlib.design_util import EasyCMOS
from hwlib.testbench import Testbench, register_test
from hwlib.basic_circuits import Inverter


class FullAdder(SubcktComponent):

    subckt_basename = "FullAdder"
    connection_names = ["a", "b", "cin", "s", "cout", "vdd", "vss"]

    def __init__(self, design):
        SubcktComponent.__init__(self, design)

    def assemble_subckt(self, design):
        e = EasyCMOS(design, "vdd", "vss")
        (par, ser, p, n) = (e.par, e.ser, e.p, e.n)

        (pnDrain, pnSource) = \
            par([
                ser([par([p("a", "8x"), p("b", "8x")]),
                     p("c", "8x")]),
                ser([p("b"),
                     p("a")])])
        design.connect(pnDrain, "vdd")

        (nnDrain, nnSource) = \
            par([
                ser([n("c", "4x"),
                     par([n("a", "4x"), n("b", "4x")])]),
                ser([n("a"),
                     n("b")])])
        design.connect(nnSource, "vss")
        design.connect(nnDrain, pnSource)

        cOutPrime = pnSource
        cOutInv = Inverter(design)
        cOutInv.vdd = "vdd"
        cOutInv.vss = "vss"

        design.connect(cOutPrime, cOutInv.input)
        cOutInv.output = "cout"

    @register_test
    class FullAdderTest(Testbench):

        def __init__(self):
            Testbench.__init__(self)

        def build_bench(self, design):
            fa = FullAdder(design)
            inputTerms = [fa.a, fa.b, fa.cin]
            outputTerms = [fa.s, fa.cout]
            design.pair({fa.vdd: design.vdd,
                         fa.vss: design.vss})
            return (inputTerms, outputTerms)


class RippleCarryAdder(SubcktComponent):

    subckt_basename = "RippleCarryAdder"
    suffix_components = ["a_width", "b_width"]

    a_width = 8
    b_width = 8

    def __init__(self, design, a_width=8, b_width=8):
        self.a_width = a_width
        self.b_width = b_width
        self.connection_names = [WArray("a", a_width),
                                 WArray("b", b_width),
                                 WArray("s", a_width + b_width),
                                 "c", "vdd", "vss"]
        SubcktComponent.__init__(self, design)

    def assemble_subckt(self, design):
        pass
