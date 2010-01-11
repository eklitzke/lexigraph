#include <sys/types.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netdb.h>

int connected_socket(char *hostname, uint16_t port)
{
    int sock;
    struct hostent *hostaddr;
    struct sockaddr_in sa;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket()");
        return -1;
    }

    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);

    hostaddr = gethostbyname(hostname);
    if (!hostaddr) {
        perror("gethostbyname()");
        goto conn_err;
    }
    memcpy(&sa.sin_addr.s_addr, hostaddr->h_addr, hostaddr->h_length);

    if (connect(sock, (struct sockaddr *) &sa, sizeof(sa)) < 0) {
        perror("connect()");
        goto conn_err;
    }
    return sock;

conn_err:
    close(sock);
    return -1;
}

int sendall(int sock, char *buffer, size_t len)
{
    printf("%s", buffer);
    return 0;
#if 0
    size_t offset;
    ssize_t ret;

    if (!len)
        len = strlen(buffer);

    offset = 0;
    while (offset < len) {
        ret = send(sock, buffer + offset, len - offset, 0);
        if (ret < 0) {
            perror("send");
            return -1;
        }
        offset += ret;
    }
    return 0;
#endif
}

/* *output will be malloced, and must be freed */
ssize_t urlencode(char *input, size_t len, char **output)
{
    char c;
    size_t i;
    size_t offset = 0;
    char *hex = "0123456789abcdef";

    if (!len)
        len = strlen(input);

    /* worst case is a string 3x the length of the input */
    *output = malloc(3 * len + 1);
    if (*output < 0) {
        perror("malloc()");
        return -1;
    }
    for (i = 0; i < len; i++) {
        c = input[i];
        if ( ('a' <= c && c <= 'z')
             || ('A' <= c && c <= 'Z')
             || ('0' <= c && c <= '9')) {
            (*output)[offset++] = c;
        } else if (c == ' ') {
            (*output)[offset++] = '+';
        } else {
            (*output)[offset++] = '%';
            (*output)[offset++] = hex[c >> 4];
            (*output)[offset++] = hex[c & 0xF];
        }
    }
    (*output)[offset] = '\0';
    return offset ;
}

void main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: add_point name float_val\n");
        exit(EXIT_FAILURE);
    }
    int sock;
    ssize_t ret;
    size_t offset;
    char *encbuf;
    char *buf;
    char cl[1000];

    sock = connected_socket("the-tempest.appspot.com", 80);
    if (sock < 0)
        goto fail_main;

    buf = malloc(1000);
    memcpy(buf, "name=", 5);
    offset = 5;

    ret = urlencode(argv[1], 0, &encbuf);
    if (ret < 0)
        goto fail_main;
    memcpy(buf + offset, encbuf, ret);
    offset += ret;

    memcpy(buf + offset, "&value=", 7);
    offset += 7;

    free(encbuf);
    ret = urlencode(argv[2], 0, &encbuf);
    if (ret < 0)
        goto fail_main;
    memcpy(buf + offset, encbuf, ret);
    offset += ret;
    buf[offset] = '\0';
    free(encbuf);

    if (sendall(sock,
                "POST /api/create/point HTTP/1.0\r\n"
                "User-Agent: add-point/1.0\r\n"
                "Connection: close\r\n"
                "Content-Type: application/x-www-form-urlencoded\r\n"
                , 0) < 0) {
        goto fail_main;
    }
    encbuf = malloc(100);
    if (encbuf < 0) {
        perror("malloc()");
        goto fail_main;
    }
    sprintf(encbuf, "Content-Length: %zd\r\n\r\n", offset);

    sendall(sock, encbuf, 0);
    sendall(sock, buf, offset);

    exit(EXIT_SUCCESS);

fail_main:
    exit(EXIT_FAILURE);
}
