#ifndef __MONITORS_HPP__
#define __MONITORS_HPP__

#include "spice_simulation.hpp"

namespace hwlib {

class PowerMonitor : public Monitor {
	std::string curr_name;
	std::string net_name;

	double weighted_total;
	double total_time;
	double max_pwr;
	double min_pwr;

public:
	PowerMonitor(std::string current, std::string net) {
		this->curr_name = current;
		this->net_name = net;
	}

	std::vector<std::string> get_vector_names() {
		return {this->curr_name,
		        this->net_name};
	}

	void init() {
		this->weighted_total = 0;
		this->total_time = 0;
		this->max_pwr = 0;
		this->min_pwr = 0;
	}

	void data(double abs_time, double tdelta, double* v) {
		double pwr = v[0] * v[1];
		if (this->total_time == 0) {
			this->min_pwr = pwr;
			this->max_pwr = pwr;
		} else {
			this->min_pwr = std::min(this->min_pwr, pwr);
			this->max_pwr = std::max(this->max_pwr, pwr);
		}
		this->weighted_total += tdelta * pwr;
		this->total_time += tdelta;
	}

	double avg() { 
		if (this->total_time == 0)
			return 0.0;
		return this->weighted_total / this->total_time;
	}
	double max() { return this->max_pwr; }
	double min() { return this->min_pwr; }
};

};

#endif // __MONITORS_HPP__