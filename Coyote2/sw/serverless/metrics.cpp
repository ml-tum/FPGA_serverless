#include "metrics.h"

Metrics *Metrics::singleton = nullptr;

constexpr float Metrics::runtime_nanos(const TaskStats &stats) {
    if(stats.reconfig_performed) {
        return std::chrono::duration_cast<std::chrono::nanoseconds>(
                stats.completion_time - stats.reconfigured_time).count();
    } else {
        return std::chrono::duration_cast<std::chrono::nanoseconds>(
                stats.completion_time - stats.launch_time).count();
    }
}

constexpr float Metrics::runtime_millis(const TaskStats &stats) {
    return runtime_nanos(stats) / 1'000'000.f;
}

constexpr float Metrics::reconfig_millis(const TaskStats &stats) {
    if(stats.reconfig_performed) {
        return std::chrono::duration_cast<std::chrono::microseconds>(
                stats.reconfigured_time - stats.launch_time).count() / 1000.f;
    } else {
        return 0.f;
    }
}

Metrics::Metrics(const string k8s_endpoint, int n_regions) :
        k8s_endpoint(k8s_endpoint),
        n_regions(n_regions),
        bitstreams(n_regions, "")
{
    curl_global_init(CURL_GLOBAL_ALL);

    singleton = this;
    reporter_thread = thread([&]() {
        while(!teardown) {
            TaskStats stats = queue.take(); //blocking
            report(stats);
        }
    });
}

Metrics::~Metrics() {
    teardown = true;
    reporter_thread.join();
    curl_global_cleanup();
}

void Metrics::push(const TaskStats &stats) {
    if(singleton== nullptr) {
        cerr<<"Metrics not initialized"<<endl;
        return;
    }

    {
        std::lock_guard<std::mutex> guard(singleton->mtx);
        singleton->bitstreams[stats.used_region] = std::to_string(stats.bitstream_config);
    }
    singleton->queue.push(stats);
}

void Metrics::report(TaskStats &stats) {
    auto completion_epoch_millis = std::chrono::duration_cast<std::chrono::milliseconds>(stats.completion_time.time_since_epoch()).count();

    string bitstreams_concat;
    bitstreams_concat.reserve(bitstreams.front().length()*n_regions*2);
    {
        std::lock_guard<std::mutex> guard(mtx);

        for(int i=0; i<bitstreams.size(); i++) {
            bitstreams_concat += i>0 ? "," : "";
            bitstreams_concat += bitstreams[i];
        }
    }

    //log runtime
    auto relative_runtime_nanos = runtime_nanos(stats);
    cout<<"Runtime: "<<relative_runtime_nanos<<" ns"<<endl;
    write_to_file(relative_runtime_nanos, stats.input_size, stats.bitstream_config, stats.used_region);

    //report, if a reconfiguration happened
    if(stats.reconfig_performed) {
        auto relative_reconfig_millis = reconfig_millis(stats);// / n_regions;
        cout<<"Report reconfiguration time: "<<(int)relative_reconfig_millis<<" ms"<<endl;
        submit_to_k8s(relative_reconfig_millis, true, bitstreams_concat, completion_epoch_millis);
    }

    //report runtime duration
    auto relative_runtime_millis = runtime_millis(stats);// / n_regions;
    cout<<"Report runtime: "<<(int)relative_runtime_millis<<" ms"<<endl;
    submit_to_k8s(relative_runtime_millis, false, bitstreams_concat, completion_epoch_millis);
}

void Metrics::submit_to_k8s(float millis, bool reconfig, const string &bitstreams_concat, long int completion_epoch_millis) {
    CURL *curl = curl_easy_init();
    if(!curl) {
        cout << "Failed to initialize curl" << endl;
        return;
    }

    char *bitstreams_safe = curl_easy_escape(curl, bitstreams_concat.c_str(), bitstreams_concat.length());
    auto post_field = + "timestamp_ms=" + std::to_string(completion_epoch_millis) +
            + "&bitstream_identifiers=" + bitstreams_safe
            + (reconfig ? "&reconfiguration_ms=" : "&duration_ms=") + std::to_string(millis);

    curl_easy_setopt(curl, CURLOPT_URL, k8s_endpoint.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_field.c_str());

    CURLcode res = curl_easy_perform(curl);

    if(res != CURLE_OK) {
        cerr<<"curl_easy_perform() failed: "<<curl_easy_strerror(res)<<endl;
    } else {
        cout<<"Metrics submitted: "<<k8s_endpoint<<"/"<<post_field<<endl;
    }

    curl_free(bitstreams_safe);
    curl_easy_cleanup(curl);
}

void Metrics::write_to_file(uint64_t runtime_nanos, size_t input_size, int bitstream, int used_region) {
    char* logfile = getenv("RUNTIMES_LOG");
    if(logfile!=NULL) {
        ofstream outfile(string(logfile), std::ios_base::app);
        outfile << "c" << bitstream << ", fpga, " << used_region << ", " << input_size << ", " << runtime_nanos << endl;
    }
}