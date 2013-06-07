#include "spice_simulation.hpp"

#include <unordered_map>
#include <algorithm>
#include <boost/foreach.hpp>
#include <cstdio>

#include "ngspice/sharedspice.h"

namespace hwlib {

bool SpiceSimulation::SpiceInUse = false;

/* Callback function called from bg thread in ngspice to transfer
   any string created by printf or puts. Output to stdout in ngspice is
   preceded by token stdout, same with stderr.*/
static int ng_getchar(char* outputreturn, void* userdata)
{
    // printf("%s\n", outputreturn);
    return 0;
}

/* Callback function called from bg thread in ngspice to transfer
   simulation status (type and progress in percent. */
static int ng_getstat(char* outputreturn, void* userdata)
{
    printf("%s\n", outputreturn);
    return 0;
}

/* Callback function called from bg thread in ngspice once per accepted data point */
static int ng_data(pvecvaluesall vdata, int numvecs, SpiceSimulation* sim)
{
	const double time = sim->time;
	const double time_step = sim->time_step;
	const auto vecs = vdata[0].vecsa;
	const int veccount = vdata[0].veccount;
	assert(veccount == numvecs);

	BOOST_FOREACH(auto miPair, sim->monitor_indexes) {
		double values[MAX_MONITOR_NODES];
		for (size_t i=0; i<MAX_MONITOR_NODES; i++) {
			int idx = miPair.second[i];
			if (idx >= 0) {
				assert(idx < veccount);
				assert(vecs[idx]->is_complex == false);
				values[i] = vecs[idx]->creal;
			}
		}

		miPair.first->data(time, time_step, values);
	}

	sim->time += sim->time_step;

	bool halt = false;
	BOOST_FOREACH(auto hc, sim->halts) {
		if (hc->halt()) {
			// HALT requested!
			halt = true;
			sim->halts_requested.push_back(hc);
		}
	}
	if (halt) {
		sim->bg_status = SpiceSimulation::HaltRequested;
		while (sim->bg_status != SpiceSimulation::HaltStarting)
			usleep(100);
		// Sleep to make sure the other thread runs the halt before I return
		usleep(1000);
	}
	return 0;
}

/* Callback function called from bg thread in ngspice once upon intialization
   of the simulation vectors)*/
static int ng_initdata(pvecinfoall intdata, SpiceSimulation* sim)
{
    int i;
    int vn = intdata->veccount;
    std::unordered_map<std::string, int> vecIdx;
    for (i = 0; i < vn; i++) {
    	std::string data = intdata->vecs[i]->vecname;
    	std::transform(data.begin(), data.end(), data.begin(), ::tolower);
    	vecIdx[data] = i;
    }

    BOOST_FOREACH(auto m, sim->monitors) {
    	auto names = m->get_vector_names();
    	assert(names.size() <= MAX_MONITOR_NODES);


    	int* idxs = new int[MAX_MONITOR_NODES];
    	for (size_t i=0; i<MAX_MONITOR_NODES; i++) {
    		if (i<names.size()) {
    			std::string name = names[i];
		    	std::transform(name.begin(), name.end(), name.begin(), ::tolower);
		    	auto fidx = vecIdx.find(name);
		    	if (fidx == vecIdx.end()) {
		    		fprintf(stderr, "Error: could not find vector: '%s'!\n", name.c_str());
		    		assert(false);
		    	}
		    	idxs[i] = fidx->second;
    		} else {
	    		idxs[i] = -1;
	    	}
    	}

    	sim->monitor_indexes[m] = idxs;
    }
    return 0;
}

static int ng_thread_runs(bool noruns, SpiceSimulation* sim)
{
	if (noruns == true) {
		if (sim->bg_status == SpiceSimulation::Running)
			sim->bg_status = SpiceSimulation::Done;
		else if (sim->bg_status == SpiceSimulation::HaltStarting)
			sim->bg_status = SpiceSimulation::Halted;
	}

    return 0;
}

/* Callback function called from bg thread in ngspice if fcn controlled_exit()
   is hit. Do not exit, but unload ngspice. */
static int ng_exit(int exitstatus, bool immediate, bool quitexit, void* userdata)
{

    if(quitexit) {
        printf("ngspice Note: Returned form quit with exit status %d\n", exitstatus);
    }

    printf("DNote: Unload ngspice\n");
    exit(exitstatus);

    return exitstatus;

}

void SpiceSimulation::InitSpice() {
	SpiceInUse = true;
	ngSpice_Init(ng_getchar, ng_getstat, ng_exit, (SendData*)ng_data,
			     (SendInitData*)ng_initdata, (BGThreadRunning*)ng_thread_runs, this);
}

void SpiceSimulation::UnInitSpice() {
	ngSpice_Init(NULL, NULL, NULL, NULL,
				 NULL, NULL, NULL);
	SpiceInUse = false;
}

void SpiceSimulation::run_trans(double time_step, double max_time) {
	this->time_step = time_step;
	if (SpiceInUse == false) {
		InitSpice();
	} else {
		assert(false && "Spice is in use!");
	}

	int rc;

	printf("Parsing netlist...\n");
	std::vector<char*> lines;
	lines.push_back(strdup(this->sim_name.c_str()));
	size_t lineBegin = 0;
	for (size_t i=0; i<this->netlist.length(); i++) {
		if (this->netlist[i] == '\n') {
			size_t len = i - lineBegin;
			if ( len >= 2 ) {
				std::string line = this->netlist.substr(lineBegin, len);
				lines.push_back(strdup(line.c_str()));
			}
			lineBegin = i + 1;
		}
	}

	char buf[1024];
	snprintf(buf, 1024, ".tran %le %le", time_step, max_time);
	lines.push_back(strdup(buf));

	lines.push_back(strdup(".end"));
	lines.push_back(NULL);

	char** linesC = new char*[lines.size()];
	copy(lines.begin(), lines.end(), linesC);

	char** lineptr = linesC;
	while (*lineptr != NULL) {
		// puts(*lineptr);
		lineptr++;
	}

	rc = ngSpice_Circ(linesC);
	assert(rc == 0 && "ngspice Error parsing netlist!");

	// Resetting halts
	halts_requested.clear();
	BOOST_FOREACH(auto hc, halts) {
		hc->reset();
	}

	BOOST_FOREACH(auto m, monitors) {
    	m->init();
	}

	printf("Running simulation...\n");
	bg_status = Running;
	this->time = 0;
	rc = ngSpice_Command((char*)"bg_run");
	assert(rc == 0 && "ngspice Command error on 'bg_run'");

	BOOST_FOREACH(auto line, lines) {
		free(line);
	}
	delete linesC;

	run_loop();
}

void SpiceSimulation::resume() {
	assert(bg_status == Halted && "Can only resume halted simulation!");

	// Resetting halts
	halts_requested.clear();
	BOOST_FOREACH(auto hc, halts) {
		hc->reset();
	}

	bg_status = Running;
	int rc = ngSpice_Command((char*)"bg_resume");
	assert(rc == 0 && "ngspice Command error on 'bg_halt'");

	run_loop();
}

void SpiceSimulation::run_loop() {
	while (bg_status == Running) {
		usleep(1000);
	}

	if (bg_status == HaltRequested) {
		bg_status = HaltStarting;
		int rc = ngSpice_Command((char*)"bg_halt");
		assert(rc == 0 && "ngspice Command error on 'bg_halt'");

		while (bg_status != Halted)
			sched_yield();
	} else if (bg_status == Done) {
		UnInitSpice();

		if (this->write_filename != "") {
			char buf[1024];
			snprintf(buf, 1024, "write %s", this->write_filename.c_str());
			printf("Writing output file\n");
			int rc = ngSpice_Command(buf);
			assert(rc == 0 && "ngspice Command error on 'write'");
		}
	}
}

void SpiceSimulation::ngspice_command(std::string cmd) {
	int rc = ngSpice_Command((char*)cmd.c_str());
	assert(rc == 0 && "ngspice Command error");
}

void SpiceSimulation::alter(std::string device, std::string param) {
	char buf[10240];
	std::transform(device.begin(), device.end(), device.begin(), ::tolower);
	snprintf(buf, 10240, "alter %s = %s", device.c_str(), param.c_str());
	int rc = ngSpice_Command(buf);
	assert(rc == 0 && "ngspice Command error on 'alter'");
}

};

// NGSpice seems to be missing this...
#include <sys/timeb.h>
extern "C" void
timediff(struct timeb *now, struct timeb *begin, int *sec, int *msec)
{

    *msec = now->millitm - begin->millitm;
    *sec = now->time - begin->time;
    if (*msec < 0) {
        *msec += 1000;
        (*sec)--;
    }
}