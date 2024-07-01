#pragma once

#include <deque>
#include <mutex>
#include <condition_variable>
#include <map>
#include <set>
#include "task.h"
#include "queue.hpp"
#include "options.h"

template<>
class Queue<Task>
{
    std::deque<Task> queue;
    std::mutex mtx;
    std::condition_variable cv;
    bool torndown = false;
    std::map<int,int> waiting;
    std::map<int,Task> next_task;


public:

    void push(const Task &elem) {
        std::lock_guard<std::mutex> lock(mtx);
        for(auto &wc : waiting) {
            //Check if bitstream is already programmed in one of the vfid's
            if(wc.second == elem.bitstreamConfig && next_task.count(wc.first)==0 && Options::get()->isVfidEnabled(wc.first)) {
                next_task[wc.first] = elem;
                cv.notify_all();
                return;
            }
        }
        queue.push_back(elem);
        cv.notify_all();
    }

    Task take(int vfid, int current_config) {
        std::unique_lock<std::mutex> lock(mtx);
        waiting[vfid] = current_config;
        cv.wait(lock, [&]() { return (Options::get()->isVfidEnabled(vfid) && !queue.empty()) || next_task.count(vfid) || torndown; });
        waiting.erase(vfid);
        if (torndown) {
            throw std::runtime_error("Queue is tearing down");
        }
        if (next_task.count(vfid)) {
            auto elem = next_task[vfid];
            next_task.erase(vfid);
            return elem;
        }
        Task elem = queue.front();
        queue.pop_front();
        return elem;
    }

    void teardown() {
        std::lock_guard<std::mutex> lock(mtx);
        // after teardown, the take() function must not return any more elements,
        // as the calling object may have been destructed
        torndown = true;
        cv.notify_all();
    }

};