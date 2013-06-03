#include "spice_simulation.hpp"

#include <boost/foreach.hpp>
#include <cassert>
#include <cstdio>

namespace hwlib {

void SpiceSimulation::add_monitor(Monitor* m) {
	assert(m != NULL && "Monitor must not be NULL");
	auto names = m->get_node_names();
	BOOST_FOREACH(auto n, names) {
		monitors[n].push_back(m);
	}
}

void SpiceSimulation::run_trans(double time_step, double max_time) {
	printf("Skipping simulation!\n");
}

};