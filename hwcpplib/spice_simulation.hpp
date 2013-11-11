#ifndef __SPICE_SIMULATION_HPP__
#define __SPICE_SIMULATION_HPP__

#include <string>
#include <vector>
#include <map>
#include <set>
#include <limits>
#include <cmath>
#include <cassert>

#include <boost/shared_ptr.hpp>

namespace hwlib {

#define MAX_MONITOR_NODES 8

class Monitor  {
public:
	virtual std::vector<std::string> get_vector_names() { return { }; }
	virtual void init() { };
	virtual void data(double abs_time, double time_diff, double* v) { };
};

typedef boost::shared_ptr<Monitor> MonitorPtr;

class HaltCondition {
protected:
	bool dohalt;
public:
	HaltCondition() : dohalt(false) { }
	virtual bool halt() { return dohalt; }
	virtual void reset() { this->dohalt = false; }

	uint64_t getid() {
		return (uint64_t)this;
	}
};

typedef boost::shared_ptr<HaltCondition> HaltConditionPtr;

class SpiceSimulation {
	static bool SpiceInUse;

	std::string sim_name;
	std::string netlist;
	std::string write_filename;

public:
	void InitSpice();
	void UnInitSpice();

	bool quiet, debug;
	int time_vec_num;
	double time;
	double time_step;
	std::set<MonitorPtr> monitors;
	std::set<HaltConditionPtr> halts;
	std::vector<HaltConditionPtr> halts_requested;
	std::map<MonitorPtr, int*> monitor_indexes;

	volatile enum Status {
		None,
		Running,
		HaltRequested,
		HaltStarting,
		Halted,
		Kill,
		Killed,
		Done
	} bg_status;

public:
	SpiceSimulation(std::string name = std::string(""),
					std::string netlist = std::string("")) {
		this->debug = false;
		this->quiet = false;
		this->sim_name = name;
		this->set_netlist(netlist);
	}

	void close() {
		UnInitSpice();
	}

	void set_output_file(std::string outfn) {
		this->write_filename = outfn;
	}

	void set_netlist(std::string netlist) {
		this->netlist = netlist;
	}
	void add_monitor(MonitorPtr m) {
		assert(m != NULL && "Monitor must not be NULL");
		this->monitors.insert(m);
	}
	void add_halt(HaltConditionPtr hc) {
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

typedef boost::shared_ptr<SpiceSimulation> SpiceSimulationPtr;

};

#endif // __SPICE_SIMULATION_HPP__