#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
using namespace boost::python;

#include "spice_simulation.hpp"
#include "monitors.hpp"
#include "halts.hpp"

namespace hwlib {

BOOST_PYTHON_MODULE(hwcpplib) {
	class_<SpiceSimulation, SpiceSimulationPtr >("spicesimulation", init<std::string, std::string>())
		.def("set_netlist", &SpiceSimulation::set_netlist)
		.def("set_output_file", &SpiceSimulation::set_output_file)
		.def("add_monitor", &SpiceSimulation::add_monitor)
		.def("add_halt", &SpiceSimulation::add_halt)
		.def("run_trans", &SpiceSimulation::run_trans)
		.def("resume", &SpiceSimulation::resume)
		.def_readwrite("debug", &SpiceSimulation::debug)
		.def_readwrite("quiet", &SpiceSimulation::quiet)
		.def_readonly("status", &SpiceSimulation::bg_status)
		.def_readonly("halts_requested", &SpiceSimulation::halts_requested)
		.def_readonly("time", &SpiceSimulation::time)
		.def_readonly("time_step", &SpiceSimulation::time_step)
		.def("ngspice_command", &SpiceSimulation::ngspice_command)
		.def("alter", &SpiceSimulation::alter)
	;
	
	enum_<SpiceSimulation::Status>("status")
		.value("none", SpiceSimulation::None)
		.value("done", SpiceSimulation::Done)
		.value("halted", SpiceSimulation::Halted)
	;

	class_<Monitor, MonitorPtr>("monitor")
	;

	class_<HaltCondition, HaltConditionPtr, boost::noncopyable>("haltcondition")
		.def("halt", &HaltCondition::halt)
		.def("getid", &HaltCondition::getid)
	;

	class_<std::vector<HaltConditionPtr> >("HaltConditionVec")
        .def(vector_indexing_suite<std::vector<HaltConditionPtr>, true >())
    ;

	class_<PowerMonitor, boost::shared_ptr<PowerMonitor>, bases<Monitor> >("powermonitor", init<std::string, std::string>())
		.def("avg", &PowerMonitor::avg)
		.def("max", &PowerMonitor::max)
		.def("min", &PowerMonitor::min)
	;

	class_<LevelHalt, boost::shared_ptr<LevelHalt>, boost::noncopyable, bases<Monitor, HaltCondition> >
		("levelhalt", init<std::string, std::string, double, bool>())
		.def("setup", &LevelHalt::setup)
		.def_readwrite("level", &LevelHalt::level)
		.def_readwrite("rising", &LevelHalt::rising)
	;
}

};