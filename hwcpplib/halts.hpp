#ifndef __HALTS_HPP__
#define __HALTS_HPP__

#include "spice_simulation.hpp"

#include <boost/enable_shared_from_this.hpp>

namespace hwlib {

class LevelHalt : public Monitor, public HaltCondition,
 				  public boost::enable_shared_from_this<LevelHalt>{
	std::string net_name;
	std::string base_net_name;
	double last_voltage;

public:
	double level;
	bool rising;

	LevelHalt(std::string net, std::string base_net,
			  double level, bool rising) {
		this->net_name = net;
		this->base_net_name = base_net;
		this->level = level;
		this->rising = rising;
	}

	void setup(SpiceSimulationPtr sim) {
		sim->add_monitor(this->shared_from_this());
		sim->add_halt(this->shared_from_this());
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
		
		// if (dohalt) {
		// 	printf("Halt requested: %s %d %lf %lf %lf\n", this->net_name.c_str(), this->rising, v, last_voltage, level);
		// } else {
		// 	printf("Halt not requested: %s %d %lf %lf %lf\n", this->net_name.c_str(), this->rising, v, last_voltage, level);
		// }
		last_voltage = v;
	}
};

};

#endif // __HALTS_HPP__