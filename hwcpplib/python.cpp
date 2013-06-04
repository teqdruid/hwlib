#include <boost/python.hpp>
using namespace boost::python;

#include "spice_simulation.hpp"

namespace hwlib {

BOOST_PYTHON_MODULE(hwcpplib) {
	class_<SpiceSimulation>("spicesimulation", init<std::string, std::string>())
		.def("set_netlist", &SpiceSimulation::set_netlist)
		.def("set_output_file", &SpiceSimulation::set_output_file)
		.def("add_monitor", &SpiceSimulation::add_monitor)
		.def("add_halt", &SpiceSimulation::add_halt)
		.def("run_trans", &SpiceSimulation::run_trans)
		.def("resume", &SpiceSimulation::resume)
		.def_readonly("status", &SpiceSimulation::bg_status)
	;

	enum_<SpiceSimulation::Status>("status")
		.value("none", SpiceSimulation::None)
		.value("done", SpiceSimulation::Done)
		.value("halted", SpiceSimulation::Halted)
	;

	class_<Monitor>("monitor")
	;

	class_<PowerMonitor, bases<Monitor> >("powermonitor", init<std::string, std::string>())
		.def("avg", &PowerMonitor::avg)
		.def("max", &PowerMonitor::max)
		.def("min", &PowerMonitor::min)
	;

	class_<HaltCondition>("haltcondition")
		.def("halt", &HaltCondition::halt)
	;

	class_<LevelHalt, bases<Monitor, HaltCondition> >("levelhalt", init<SpiceSimulation*, std::string, double, bool>())
		.def_readwrite("level", &LevelHalt::level)
		.def_readwrite("rising", &LevelHalt::rising)
	;
}

};