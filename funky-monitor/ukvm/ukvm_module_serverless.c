
#define _GNU_SOURCE
#include <assert.h>
#include <err.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include "ukvm.h"

#include "ukvm_serverless.h"

static void hypercall_serverless_test(struct ukvm_hv *hv, ukvm_gpa_t gpa)
{
    FILE *fd;
    time_t curtime;

    printf("\n*** entering hypercall_serverless_test...***\n\n");
    fd = fopen("/home/martin/hypercall_serverless.txt", "aw");
    if(fd==NULL) {
        printf("\nCould not open file\n");
    } else
    {
        time(&curtime);
        fputs("hello ", fd);
        fputs(ctime(&curtime), fd);
        fclose(fd);    
    }
}

static void hypercall_serverless_set_csr(struct ukvm_hv *hv, ukvm_gpa_t gpa)
{
    struct ukvm_serverless_set_csr *set_csr = UKVM_CHECKED_GPA_P(hv, gpa, sizeof (struct ukvm_serverless_set_csr));

    serverless_set_csr(set_csr->offset, set_csr->value);
    set_csr->ret = 0;
}

static void hypercall_serverless_load_bitstream(struct ukvm_hv *hv, ukvm_gpa_t gpa)
{
    struct ukvm_serverless_load_bitstream *load_bitstream = UKVM_CHECKED_GPA_P(hv, gpa, sizeof (struct ukvm_serverless_load_bitstream));

    serverless_load_bitstream(load_bitstream->config);
    load_bitstream->ret = 0;
}

static void hypercall_serverless_map_memory(struct ukvm_hv *hv, ukvm_gpa_t gpa)
{
    printf("pid=%u\n", getpid());

    struct ukvm_serverless_map_memory *map_memory = UKVM_CHECKED_GPA_P(hv, gpa, sizeof (struct ukvm_serverless_map_memory));

    size_t len = map_memory->len;
    size_t input_len = map_memory->input_len;
    size_t output_len = map_memory->output_len;
    void *ptr = UKVM_CHECKED_GPA_P(hv, map_memory->addr, len);

    serverless_map_memory(ptr, len, input_len, output_len);

    map_memory->ret = 0;
}

static void hypercall_serverless_exec(struct ukvm_hv *hv, ukvm_gpa_t gpa)
{
    struct ukvm_serverless_exec *ukvm_serverless_exec = UKVM_CHECKED_GPA_P(hv, gpa, sizeof (struct ukvm_serverless_exec));

    serverless_exec();

    //sleep(5);
    
    ukvm_serverless_exec->ret = 0;
}

static int handle_cmdarg(char *cmdarg)
{
    return 0;
}

static int setup(struct ukvm_hv *hv)
{
    serverless_connect();

    assert(ukvm_core_register_hypercall(UKVM_HYPERCALL_SERVERLESS_TEST,
                hypercall_serverless_test) == 0);
    assert(ukvm_core_register_hypercall(UKVM_HYPERCALL_SERVERLESS_SET_CSR,
                hypercall_serverless_set_csr) == 0);
    assert(ukvm_core_register_hypercall(UKVM_HYPERCALL_SERVERLESS_LOAD_BITSTREAM,
                hypercall_serverless_load_bitstream) == 0);
    assert(ukvm_core_register_hypercall(UKVM_HYPERCALL_SERVERLESS_MAP_MEMORY,
                hypercall_serverless_map_memory) == 0);
    assert(ukvm_core_register_hypercall(UKVM_HYPERCALL_SERVERLESS_EXEC,
                hypercall_serverless_exec) == 0);

    return 0;
}

static char *usage(void)
{
    return "--serverless=test (TODO)";
}

struct ukvm_module ukvm_module_serverless = {
    .name = "serverless",
    .setup = setup,
    .handle_cmdarg = handle_cmdarg,
    .usage = usage
};
