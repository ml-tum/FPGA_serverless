#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

struct timespec ts_measure_start, ts_measure_end;
long long int measure_nanos=0;

void measure_start() {
    clock_gettime(CLOCK_REALTIME, &ts_measure_start);
}

void measure_end() {
    clock_gettime(CLOCK_REALTIME, &ts_measure_end);
    measure_nanos += (ts_measure_end.tv_sec-ts_measure_start.tv_sec)*(long long int)1e9 
        + (ts_measure_end.tv_nsec-ts_measure_start.tv_nsec);
}

void measure_write(const char* application, const char* plattform, size_t input_size) {
    assert(strcmp(plattform,"cpu")==0 || strcmp(plattform,"fpga"));

    char* homedir = getenv("HOME");
    char path[256];
    snprintf(path, sizeof path, "%s/output/benchmark.csv", homedir);

    FILE *fd;
    fd = fopen(path, "a");
    fprintf(fd, "%s, %s, %ld, %lld\n", application, plattform, input_size, measure_nanos);
    fclose(fd);

    fprintf(stderr, "Elapsed time: %lld ns\n", measure_nanos);
}
