#include <iostream>
#include <cassert>
#include <vector>
#include "MurmurHash3.h"
#include "hll.h"
#include "util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output)
{
    stringstream stst;
    stst<<input;

    vector<int32_t> vec;
    int32_t value;
    while(stst>>value) {
        vec.push_back(value);
    }

    hll_t h;
    int ret;

    ret = hll_init(14, &h);
    assert(ret==0);

    for(int v : vec) {
        // see hll_add(hll_t *h, char *key)
        uint64_t out[2];
        MurmurHash3_x64_128(&v, sizeof(v), 0, &out);
        hll_add_hash(&h, out[1]);
    }

    double s = hll_size(&h);
    output<<s<<endl;

    hll_destroy(&h);
}
