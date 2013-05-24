#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Simulation:

    def __init__(self, time, outfn):
        self.time = time
        self.outfn = outfn

    def print_netlist(self, stream):
        stream.write("""
.control
tran 10p {time}
write {outfn}
.endc
.end
""".format(**self.__dict__))
