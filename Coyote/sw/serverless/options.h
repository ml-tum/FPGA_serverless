#pragma once

#include <string>
#include <iostream>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <sstream>

class Options {
    static Options *singleton;

    std::mutex mtx;
    std::thread reader_thread;
    bool teardown = false;

    int limit_regions = 0; // 0 = use all regions
    bool always_reconfigure = false;


public:
    static Options* get();

    Options();
    ~Options();

    bool isVfidEnabled(int vfid);
    bool isAlwaysReconfigure();

private:
    void readerLoop();
    void apply(std::string option, std::string value);
    void printOptions();

};
