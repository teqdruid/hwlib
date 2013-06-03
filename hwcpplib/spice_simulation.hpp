#ifndef __SPICE_SIMULATION_HPP__
#define __SPICE_SIMULATION_HPP__

#include <string>
#include <vector>
#include <map>

namespace hwlib {

#define MAX_MONITOR_NODES 8

class Monitor {
public:
	virtual std::vector<std::string> get_node_names() { return { }; }
	virtual void init() { };
	virtual void data(double abs_time, double time_diff, double* v) { };
};

class SpiceSimulation {
	std::string sim_name;
	std::string netlist;

	std::map<std::string, std::vector<Monitor*> > monitors;
	std::map<Monitor*, int* > monitor_indexes;

public:
	SpiceSimulation(std::string name = std::string(""),
					std::string netlist = std::string("")) {
		this->sim_name = name;
		this->set_netlist(netlist);
	}

	void set_netlist(std::string netlist) {
		this->netlist = netlist;
	}
	void add_monitor(Monitor* m);

	// Run a transient analysis with particular time step and
	//   maximum amount of simulated time in seconds
	void run_trans(double time_step, double max_time);
};

class PowerMonitor : public Monitor {
	std::string dev_name;
	std::string net_name;

	double weighted_total;
	double total_time;
	double max_pwr;
	double min_pwr;

public:
	PowerMonitor(std::string dev, std::string net) {
		this->dev_name = dev;
	}

	std::vector<std::string> get_node_names() {
		return {"i(" + this->dev_name + ")",
		        "v(" + this->net_name + ")"};
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

#endif // __SPICE_SIMULATION_HPP__