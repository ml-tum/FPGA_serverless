#pragma once

#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <fstream>
#include <curl/curl.h>
#include "task.h"
#include "queue.hpp"

class Metrics {
    static constexpr auto COLLECTION_WINDOW = std::chrono::minutes(5);
    static Metrics *singleton;


    std::mutex mtx;
    vector<string> bitstreams;

    Queue<TaskStats> queue;

    string k8s_endpoint;
    int n_regions;
    std::thread reporter_thread;
    bool teardown = false;

public:
    Metrics(const string k8s_endpoint, int n_regions);
    ~Metrics();

    constexpr static float runtime_millis(const TaskStats &stats);
    constexpr static float runtime_nanos(const TaskStats &stats);
    constexpr static float reconfig_millis(const TaskStats &stats);
    static void push(const TaskStats &stats);

    void report(TaskStats &stats);
    void submit_to_k8s(float millis, bool reconfig, const string &bitstreams_concat, long completion_epoch_millis);
    void write_to_file(uint64_t runtime_nanos, size_t input_size, int bitstream, int used_region);
};
