#include "options.h"

Options *Options::singleton = nullptr;

Options::Options() {
    singleton = this;
    reader_thread = std::thread([&]() {
        readerLoop();
    });
}

Options::~Options() {
    teardown = true;
    reader_thread.join();
}

Options *Options::get() {
    if (Options::singleton == nullptr) {
        Options::singleton = new Options();
    }
    return Options::singleton;
}

void Options::readerLoop() {
    std::string cmd;
    while (!teardown && std::cin >> cmd) {
        int delim = cmd.find('=');
        if (delim == std::string::npos) {
            std::cout << "[OPTIONS] Unknown command" << std::endl;
        } else {
            std::string name = cmd.substr(0, delim);
            std::string value = cmd.substr(delim + 1);
            apply(name, value);
        }
        printOptions();
    }
}

void Options::apply(std::string option, std::string value) {
    int number;
    bool boolean;
    auto stst = std::istringstream(value);
    stst >> std::boolalpha;

    if (option == "LIMIT_REGIONS" && stst >> number && (number >= 0 && number <= 16)) {
        limit_regions = number;
    } else if (option == "ALWAYS_RECONFIGURE" && stst >> boolean) {
        always_reconfigure = boolean;
    } else {
        std::cout << "[OPTIONS] Unknown command or value" << std::endl;
    }
}

void Options::printOptions() {
    std::cout << "[OPTIONS] Current options: \n"
              << "[OPTIONS] LIMIT_REGIONS=" << limit_regions << " \n"
              << "[OPTIONS] ALWAYS_RECONFIGURE=" << std::boolalpha << always_reconfigure
              << std::endl;
}

bool Options::isVfidEnabled(int vfid) {
    int limit = Options::get()->limit_regions;
    return limit == 0 || vfid < limit;
}

bool Options::isAlwaysReconfigure() {
    return Options::get()->always_reconfigure;
}