#ifndef __HALTS_HPP__
#define __HALTS_HPP__

#include "spice_simulation.hpp"

namespace hwlib {

class LevelHalt : public Monitor, public HaltCondition {
	std::string net_name;
	std::string base_net_name;
	double last_voltage;

public:
	double level;
	bool rising;

	LevelHalt(SpiceSimulation* sim,
			  std::string net, std::string base_net,
			  double level, bool rising) {
		this->net_name = net;
		this->base_net_name = base_net;
		this->level = level;
		this->rising = rising;

		sim->add_monitor(this);
		sim->add_halt(this);
	}

	std::vector<std::string> get_vector_names() {
		return {this->net_name, this->base_net_name};
	}

	void init() {
		this->last_voltage = std::numeric_limits<double>::infinity();
	}

	void data(double abs_time, double tdelta, double* va) {
		// printf("%le, %d, %le, %le\n", level, rising, last_voltage, va[0]);
		double v = va[0] - va[1];
		if (std::isinf(last_voltage)) {
			last_voltage = v;
			return;
		}

		if (rising && v >= level && last_voltage < level) {
			dohalt = true;
		} else if (!rising && v <= level && last_voltage > level) {
			dohalt = true;
		}
		last_voltage = v;
	}
};

};

#endif // __HALTS_HPP__