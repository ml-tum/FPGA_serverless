#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <malloc.h>
#include <mm_malloc.h>

#define MSG_SIZE 1024
const char* SOCKET_NAME = "/tmp/serverless.sock";
char MSG_BUF[MSG_SIZE];
int msg_ptr = 0;
int sockfd = -1;

void serverless_connect() {
    struct sockaddr_un addr;
    int sfd = socket(AF_UNIX, SOCK_STREAM, 0);
    printf("Client socket fd = %d\n", sfd);
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
    if(sockfd<0) {
        printf("socket not connected");
        return;
    }

    int len = strlen(str);
    if(msg_ptr+len >= MSG_SIZE) {
        printf("message too long\n");
        return;
    }
    if(len==0 || str[len-1] != '\n') {
        printf("message must end in newline\n");
        return;
    }

    memcpy(MSG_BUF+msg_ptr, str, len);
    msg_ptr += len;
}

void serverless_flush_sock() {
    if(sockfd<0) {
        printf("socket not connected");
        return;
    }

    MSG_BUF[msg_ptr] = '\0';
    msg_ptr++;

    //submit
    printf("Writing:\n%s\n", MSG_BUF);
    if(write(sockfd, MSG_BUF, MSG_SIZE) == -1) {
        perror("write() error");
        return;
    }

    //wait for response
    memset(MSG_BUF, 0, sizeof(MSG_BUF));
    int bytes = read(sockfd, MSG_BUF, MSG_SIZE);
    if(bytes <= 0) {
        perror("read() error");
        return;
    }
    printf("got response: %s\n", MSG_BUF);

    //reset
    msg_ptr = 0;
}

void serverless_set_csr(uint32_t offset, uint64_t value)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "SET_CSR %u %lu\n", offset, value);
    serverless_write_sock(str);
}

void serverless_load_bitstream(uint32_t config)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "BITSTREAM %u\n", config);
    serverless_write_sock(str);
}

void serverless_map_memory(void *addr, size_t len, size_t input_len, size_t output_len)
{
    char str[MSG_SIZE];
    snprintf(str, sizeof(str), "USERMAP %lu %lu %lu %lu\n", (uint64_t)addr, len, input_len, output_len);
    serverless_write_sock(str);
}

void serverless_exec() {
    serverless_write_sock("LAUNCH\n");
    serverless_flush_sock();
}
