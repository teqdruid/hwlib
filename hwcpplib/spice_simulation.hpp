#ifndef __SPICE_SIMULATION_HPP__
#define __SPICE_SIMULATION_HPP__

#include <string>
#include <vector>
#include <map>
#include <set>
#include <limits>
#include <cmath>

#include <cassert>

namespace hwlib {

#define MAX_MONITOR_NODES 8

class Monitor {
public:
	virtual std::vector<std::string> get_vector_names() { return { }; }
	virtual void init() { };
	virtual void data(double abs_time, double time_diff, double* v) { };
};

class HaltCondition {
protected:
	bool dohalt;
public:
	HaltCondition() : dohalt(false) { }
	virtual bool halt() { return dohalt; }
	virtual void reset() { this->dohalt = false; }
};

class SpiceSimulation {
	static bool SpiceInUse;
	void InitSpice();
	void UnInitSpice();

	std::string sim_name;
	std::string netlist;
	std::string write_filename;

public:
	double time_step, time;
	std::set<Monitor*> monitors;
	std::set<HaltCondition*> halts;
	std::map<Monitor*, int*> monitor_indexes;

	volatile enum Status {
		None,
		Running,
		HaltRequested,
		HaltStarting,
		Halted,
		Done
	} bg_status;

public:
	SpiceSimulation(std::string name = std::string(""),
					std::string netlist = std::string("")) {
		this->sim_name = name;
		this->set_netlist(netlist);
	}

	void set_output_file(std::string outfn) {
		this->write_filename = outfn;
	}

	void set_netlist(std::string netlist) {
		this->netlist = netlist;
	}
	void add_monitor(Monitor* m) {
		assert(m != NULL && "Monitor must not be NULL");
		this->monitors.insert(m);
	}
	void add_halt(HaltCondition* hc) {
		assert(hc != NULL && "HaltCondition mustn't be NULL!");
		this->halts.insert(hc);
	}

	void ngspice_command(std::string cmd);
	void alter(std::string device, std::string param);

	// Run a transient analysis with particular time step and
	//   maximum amount of simulated time in seconds
	void run_trans(double time_step, double max_time);
	void resume();

private:
	void run_loop();
};

};

#endif // __SPICE_SIMULATION_HPP__