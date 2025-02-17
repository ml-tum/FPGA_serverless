#include <iostream>
#include <string>
#include <sstream>
#include <signal.h>
#include <unistd.h>
#include <x86intrin.h>
#include <boost/program_options.hpp>
#include <sys/socket.h>
#include <sys/un.h>

#include "consumer.h"
#include "task.h"
#include "printer.h"
#include "metrics.h"
#include "queue_task.hpp"

using namespace std;
using namespace fpga;

constexpr int LISTEN_BACKLOG = 10;
const char* SOCKET_NAME = "/tmp/serverless.sock";
//const string K8S_ENDPOINT = "https://engpus71dlfvk.x.pipedream.net/";
const string K8S_ENDPOINT = "http://localhost:8080/";
const int MSG_SIZE=1024;
const int MAX_REGIONS=15;

const string RESP_OK = "OK";
const string OP_BITSTREAM = "BITSTREAM";
const string OP_SET_CSR = "SET_CSR";
const string OP_LAUNCH = "LAUNCH";
const string OP_USERMAP = "USERMAP";

Queue<Task> taskQueue;
vector<Consumer*> consumers;
int n_regions=0;
bool teardown=false;

vector<string> tokenize(const string str) {
    vector<string> result;
    stringstream stst(str);
    string val;
    while(stst>>val) {
        if(val.find('\0') != string::npos) {
            val = val.substr(0, val.find('\0'));
        }
        result.push_back(val);
    }
    return result;
}

void sig_handler(int signum) {
    cout<<"Signal received, signum="<<signum<<endl;
    teardown=true;
    taskQueue.teardown();

    for(auto c : consumers) {
        // destruction of consumer will eventually instruct the driver to free mapped memory
        c->join();
        delete c;
    }
}

void sendOk(int fd) {
    char msg[MSG_SIZE] = {0};
    strncpy(msg, RESP_OK.c_str(), MSG_SIZE);
    if(write(fd, msg, MSG_SIZE) == -1) {
        cerr<<"write() error"<<endl;
    }
}

void receiver(int cfd) {
    Printer("fd", cfd)<<"Receiver for fd="<<cfd<<endl;

    char buf[MSG_SIZE];
    pid_t clientPid=0;
    struct ucred ucred;
    socklen_t ucred_len = sizeof(ucred);
    if(getsockopt(cfd, SOL_SOCKET, SO_PEERCRED, &ucred, &ucred_len) == -1) {
        Printer("fd", cfd)<<"getsockopt() failed"<<endl;
    } else {
        clientPid = ucred.pid;
        Printer("fd", cfd)<<"client pid="<<clientPid<<endl;
    }

    Task task;
    task.clientPid = clientPid;
    task.clientFd = cfd;

    ssize_t bytes;
    while((bytes = read(cfd, buf, MSG_SIZE)) > 0) {
        if(teardown) {
            return;
        }

        auto cmd = string(buf, bytes);
        auto split = tokenize(cmd);
        Printer("fd", cfd)<<"Received cmd:\n"<<cmd<<endl;

        auto itSplit = split.begin();
        while(itSplit != split.end()) {

            auto prevItSplit = itSplit;

            if(*itSplit==OP_BITSTREAM) {
                int config = stoi(*(++itSplit));
                Printer("fd", cfd)<<"addBitstream, config="<<config<<endl;
                task.bitstreamConfig = config;
                //sendOk(cfd);
                itSplit++;
            }

            if(*itSplit==OP_SET_CSR) {
                uint32_t regNr = stoul(*(++itSplit));
                uint64_t value = stoull(*(++itSplit));
                Printer("fd", cfd)<<"set csr, regNr="<<regNr<<", value="<<value<<endl;
                task.csrMap[regNr] = value;
                //sendOk(cfd);
                itSplit++;
            }

            if(*itSplit==OP_USERMAP) {
                uint64_t vaddr = stoull(*(++itSplit));
                uint32_t len = stoul(*(++itSplit));
                uint32_t input_len = stoul(*(++itSplit));
                uint32_t output_len = stoul(*(++itSplit));
                Printer("fd", cfd)<<"usermap, vaddr="<<hex<<vaddr<<dec<<", len="<<len<<", input_len="<<input_len<<", output_len="<<output_len<<endl;
                task.mappedMem.emplace_back(vaddr, len);
                if(input_len > 0) {
                    task.inputMem = {vaddr, input_len};
                }
                if(output_len > 0) {
                    task.outputMem = {vaddr, output_len};
                }
                //sendOk(cfd);
                itSplit++;
            }

            if(*itSplit==OP_LAUNCH) {
                if (task.bitstreamConfig < 0) {
                    Printer("fd", cfd) << "error: no operator loaded!" << endl;
                } else {
                    Printer("fd", cfd) << "Enqueue" << endl;
                    task.enqueue_time = std::chrono::system_clock::now();
                    taskQueue.push(task);

                    // reset task, so connection can be re-used
                    task = {};
                    task.clientPid = clientPid;
                    task.clientFd = cfd;
                }
                itSplit++;
            }

            if(itSplit == prevItSplit) {
                Printer("fd", cfd) << "unknown command: "<< *itSplit << endl;
                itSplit++;
            }
        }

        Printer("fd", cfd)<<"Completed cmd"<<endl;
    }
    close(cfd);
}

int main(int argc, char *argv[])
{
    struct sigaction int_handler;
    int_handler.sa_handler=sig_handler;
    sigaction(SIGINT,&int_handler,0);

//
//    boost::interprocess::named_mutex::remove("vfpga_mtx_user_" + vfid);
//    boost::interprocess::named_mutex::remove("vfpga_mtx_data_" + vfid);
//    boost::interprocess::named_mutex::remove("vfpga_mtx_mem_" + vfid);


    for(int i=0; i<MAX_REGIONS; i++) {
        string dev_file = "/dev/fpga" + to_string(i);
        bool file_exists = access( dev_file.c_str(), F_OK ) != -1;
        if(file_exists) {
            cerr<<"Creating consumer for vFPGA at "<<dev_file<<endl;
            consumers.push_back(new Consumer(i, &taskQueue));
            n_regions++;
        }
    }

    if(consumers.empty()) {
        cout<<"Could not acquire any vFPGA, exiting..."<<endl;
        exit(EXIT_FAILURE);
    }

    cerr<<"Opening socket"<<endl;

    struct sockaddr_un addr;
    int sockfd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sockfd == -1) {
        perror("socket()");
        exit(EXIT_FAILURE);
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_NAME, sizeof(addr.sun_path)-1);
    unlink(addr.sun_path); //delete, if already exists

    if(bind(sockfd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        cerr<<"bind() error"<<endl;
        exit(EXIT_FAILURE);
    }

    if (chmod(addr.sun_path, strtol("0777", 0, 8)) == -1) {
        cerr<<"chmod error"<<endl;
        exit(EXIT_FAILURE);
    }

    if(listen(sockfd, LISTEN_BACKLOG) == -1) {
        cerr<<"listen() error"<<endl;
        exit(EXIT_FAILURE);
    }

    Metrics metrics(K8S_ENDPOINT, n_regions);

    while(1) {
        Printer()<<"main loop"<<endl;
        if(teardown) {
            return EXIT_SUCCESS;
        }
        Printer()<<"Calling accept()"<<endl;
        int cfd = accept(sockfd, NULL, NULL);
        Printer()<<"accept() returned, fd="<<cfd<<endl;
        if(teardown || cfd==-1) {
            return EXIT_SUCCESS;
        }

        new std::thread(receiver, cfd);
//        receiver(cfd);

    }

}
