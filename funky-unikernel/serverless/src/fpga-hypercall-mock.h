#pragma once

#include <assert.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <iostream>
#include <sstream>
#include <string_view>
#include <vector>
#include <cstring>
#include <ctime>

#define MSG_SIZE 1024
const char* SOCKET_NAME = "/tmp/serverless.sock";
char MSG_BUF[MSG_SIZE];
int msg_index = 0;
int sockfd = -1;

void func(std::string_view &input, std::stringstream &output);

void serverless_connect() {
    struct sockaddr_un addr;
    int sfd = socket(AF_UNIX, SOCK_STREAM, 0);
    fprintf(stderr, "Client socket fd = %d\n", sfd);
    if(sfd==-1) {
        perror("socket() error");
        return;
    }

    memset(&addr, 0, sizeof(struct sockaddr_un));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_NAME, sizeof(addr.sun_path)-1);

    if(connect(sfd, (struct sockaddr*) &addr, sizeof(addr))==-1) {
        perror("connect() error");
        return;
    }

    sockfd = sfd;
}

void serverless_write_sock(const char* const str) {
    int len = strlen(str);
    if(msg_index+len >= MSG_SIZE) {
        fprintf(stderr, "message too long\n");
        exit(1);
    }
    if(len==0 || str[len-1] != '\n') {
        fprintf(stderr, "message must end in newline\n");
        exit(1);
    }

    memcpy(MSG_BUF+msg_index, str, len);
    msg_index += len;
}

void serverless_flush_sock() {
    if(sockfd<0) {
        fprintf(stderr, "socket not connected");
        exit(1);
    }

    MSG_BUF[msg_index] = '\0';
    msg_index++;

    //submit
    fprintf(stderr, "writing:\n%s\n", MSG_BUF);
    if(write(sockfd, MSG_BUF, MSG_SIZE) == -1) {
        perror("write() error");
        return;
    }

    //wait for response
    memset(MSG_BUF, 0, sizeof(MSG_BUF));
    int bytes = read(sockfd, MSG_BUF, MSG_SIZE);
    if(bytes <= 0) {
        perror("read() error");
    } else {
        fprintf(stderr, "got response: %s\n", MSG_BUF);
    }

    //reset
    msg_index = 0;
}

void solo5_serverless_set_csr(uint32_t offset, uint64_t value)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "SET_CSR %u %lu\n", offset, value);
    serverless_write_sock(str);
}

void solo5_serverless_load_bitstream(uint32_t config)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "BITSTREAM %u\n", config);
    serverless_write_sock(str);
}

void solo5_serverless_map_memory(void *addr, size_t len, size_t input_len, size_t output_len)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "USERMAP %lu %lu %lu %lu\n", (uint64_t)addr, len, input_len, output_len);
    serverless_write_sock(str);
}

void solo5_serverless_exec() {
	serverless_connect();
    serverless_write_sock("LAUNCH\n");
    serverless_flush_sock();
}

long long int getNanos() {
  timespec ts;
  long long int nanos;
  clock_gettime(CLOCK_REALTIME, &ts);
  nanos = ts.tv_sec*1e9 + ts.tv_nsec;
  return nanos;
}

int main() {
    std::stringstream input, output;
    input << std::cin.rdbuf();

    std::string input_str = input.str();
    std::string_view input_sv{ input_str };
    long long int timer = getNanos();
    func(input_sv, output);
    timer = getNanos()-timer;
    std::cout << output.str();

    std::cerr<<"Elapsed time: "<<timer<<" ns";

    return 0;
}