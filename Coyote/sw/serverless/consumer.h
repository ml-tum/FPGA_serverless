#pragma once

#include <thread>
#include <string>
#include <map>

#include "queue.hpp"
#include "queue_task.hpp"
#include "executor.h"
#include "task.h"

class Consumer {

    int vfid;
    Queue<Task> *queue;
    Executor executor;

    std::thread looper;
    std::map<std::string,int32_t> operatorMap;
    int32_t currentConfig = -1;

    void loop();

public:
    Consumer(int vfid, Queue<Task> *queue);
    ~Consumer();

    void join();

};