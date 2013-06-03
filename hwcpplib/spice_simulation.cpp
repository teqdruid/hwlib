#include "spice_simulation.hpp"

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
    printf("%s\n", outputreturn);
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
	return 0;
}

/* Callback function called from bg thread in ngspice once upon intialization
   of the simulation vectors)*/
static int ng_initdata(pvecinfoall intdata, SpiceSimulation* sim)
{
    int i;
    int vn = intdata->veccount;
    for (i = 0; i < vn; i++) {
        printf("vector: %s\n", intdata->vecs[i]->vecname);
        /* find the location of v(2) */
        // if (cieq(intdata->vecs[i]->vecname, "v(2)"))
            // vecgetnumber = i;
    }
    return 0;
}

static int ng_thread_runs(bool noruns, void* userdata)
{
    if (noruns)
        printf("bg not running\n");
    else
        printf("bg running\n");

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
    ngSpice_Command((char*)"bg_pstop");

    return exitstatus;

}

void SpiceSimulation::InitSpice() {
	SpiceInUse = true;
	ngSpice_Init(ng_getchar, ng_getstat, ng_exit, (SendData*)ng_data,
			     (SendInitData*)ng_initdata, ng_thread_runs, this);
}

void SpiceSimulation::UnInitSpice() {
	ngSpice_Init(NULL, NULL, NULL, NULL,
				 NULL, NULL, NULL);
	SpiceInUse = false;
}

void SpiceSimulation::run_trans(double time_step, double max_time) {
	if (SpiceInUse == false) {
		InitSpice();
	} else {
		assert(false && "Spice is in use!");
	}

	printf("Skipping simulation!\n");


	UnInitSpice();
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