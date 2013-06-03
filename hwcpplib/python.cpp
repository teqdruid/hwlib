#include <boost/python.hpp>
using namespace boost::python;

#include "spice_simulation.hpp"

namespace hwlib {

BOOST_PYTHON_MODULE(hwcpplib) {
	class_<SpiceSimulation>("spicesimulation", init<std::string, std::string>())
		.def("set_netlist", &SpiceSimulation::set_netlist)
		.def("add_monitor", &SpiceSimulation::add_monitor)
		.def("run_trans", &SpiceSimulation::run_trans)
	;

	class_<Monitor>("monitor")
	;

	class_<PowerMonitor, bases<Monitor> >("powermonitor", init<std::string, std::string>())
		.def("avg", &PowerMonitor::avg)
		.def("max", &PowerMonitor::max)
		.def("min", &PowerMonitor::min)
	;
}

};