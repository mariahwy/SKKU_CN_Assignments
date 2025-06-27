#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdlib>
#ifdef _WIN32
#include <winsock2.h>
#include <windows.h> // For ShellExecute
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8000
#define BUFFER_SIZE 1024

int main() {
#ifdef _WIN32
    WSADATA wsa;
    WSAStartup(MAKEWORD(2,2), &wsa);
#endif

    // 1. Create socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "Socket creation failed\n";
        return 1;
    }

    // 2. Define server address
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // 3. Connect to server
    if (connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "Connection failed\n";
        return 1;
    }
    std::cout << "[Client 1] Connected to Local Server\n";

    // 4. Send video request
    const char* filename = "Video_2025.mp4\n";
    send(sock, filename, strlen(filename), 0);

    // 5. Save to file
    const char* output_file = "received_video_2025.mp4";
    std::ofstream outFile(output_file, std::ios::binary);
    if (!outFile) {
        std::cerr << "Failed to open output file\n";
#ifdef _WIN32
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return 1;
    }

    char buffer[BUFFER_SIZE];
    int bytesReceived;
    while ((bytesReceived = recv(sock, buffer, BUFFER_SIZE, 0)) > 0) {
        outFile.write(buffer, bytesReceived);
    }

    std::cout << "[Client 1] Video saved as '" << output_file << "'\n";
    outFile.close();

#ifdef _WIN32
    closesocket(sock);
    WSACleanup();
#else
    close(sock);
#endif

    // 6. Run viewer_video.py from C++ (Python script must be in same folder)
#ifdef _WIN32
    std::cout << "[Client 1] Launching viewer...\n";
    ShellExecuteA(NULL, "open", "python", 
        "viewer_video.py received_video_2025.mp4 \"FROM CACHE SERVER - CLIENT 1\"", 
        NULL, SW_SHOWNORMAL);
#else
    system("python3 viewer_video.py received_video_2025.mp4 \"FROM CACHE SERVER - CLIENT 1\"");
#endif

    return 0;
}
