#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simulation import Simulation
from design import Design
from basics import Voltage, Resistor
from basic_circuits import Inverter
from sys import stdout


class Testbench (Simulation):

    RegisteredTests = dict()

    def __init__(self, clk_per="10n", vdd_voltage=1.0, output_load="4x"):
        self.design = Design(vdd_voltage)
        d = self.design
        self.power_sources = [d.vpwr]
        (self.inputTerms, self.outputTerms) = self.build_bench(d)
        Simulation.__init__(
            self, self.design, "1", str(self.__class__), clk_per)

        for it in self.inputTerms:
            drvr = Voltage(d, vdd_voltage)
            drvrInv = Inverter(d)
            d.pair({drvr.plus: drvrInv.input,
                    drvrInv.output: it,
                    drvr.minus: d.vss})

        for ot in self.outputTerms:
            loadInv = Inverter(d, width=output_load)
            rload = Resistor(d, "1000000000")
            d.pair({loadInv.input: ot,
                    loadInv.output: rload.a,
                    rload.b: d.vss})

    def printNetlist(self, stream=stdout):
        self.design.print_netlist(stream)

    def run(self):
        pass

    def build_bench(self, design):
        raise NotImplementedError()


def register_test(c):
    Testbench.RegisteredTests[str(c)] = c
    return c
