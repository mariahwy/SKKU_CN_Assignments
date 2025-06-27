#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>  // ShellExecute
#pragma comment(lib, "ws2_32.lib")
#else
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#endif

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8000
#define BUFFER_SIZE 1024

int main() {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    int sock;
    struct sockaddr_in serverAddr;
    char buffer[BUFFER_SIZE];

    // 1. Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Socket creation failed");
        return 1;
    }

    // 2. Setup server address
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // 3. Connect
    if (connect(sock, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("Connection failed");
#ifdef _WIN32
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return 1;
    }

    printf("[Client 2] Connected to local server\n");

    // 4. Send video name
    const char *filename = "Video_2024.mp4";
    send(sock, filename, strlen(filename), 0);

    // 5. Open output file
    const char *output_name = "received_video_2024.mp4";
    FILE *fp = fopen(output_name, "wb");
    if (fp == NULL) {
        perror("File open failed");
#ifdef _WIN32
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return 1;
    }

    // 6. Receive and write to file
    int bytesReceived;
    int totalBytes = 0;
    while ((bytesReceived = recv(sock, buffer, BUFFER_SIZE, 0)) > 0) {
        fwrite(buffer, 1, bytesReceived, fp);
        totalBytes += bytesReceived;
    }

    printf("[Client 2] Video saved as '%s' (%d bytes)\n", output_name, totalBytes);
    fclose(fp);

#ifdef _WIN32
    closesocket(sock);
    WSACleanup();
#else
    close(sock);
#endif

    // 7. Run viewer_video.py (Windows only)
#ifdef _WIN32
    printf("[Client 2] Launching viewer...\n");
    ShellExecuteA(NULL, "open", "python",
        "viewer_video.py received_video_2024.mp4 \"FROM GLOBAL SERVER - CLIENT 2\"",
        NULL, SW_SHOWNORMAL);
#endif

    return 0;
}
