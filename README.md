# SKKU_CN_Assignments

### PA5

This project implements a client-server video streaming system featuring a global server, a local server, and three clients. The system supports both recorded video playback and live streaming, with caching and real-time data forwarding mechanisms.

📌 Key Functionalities:
Video Caching and Delivery

The local server caches recorded videos after the first request to reduce latency for subsequent clients.

Global Server Communication

If a requested video is not available locally, the local server contacts the global server, retrieves the video or live stream, and delivers it to the client.

Client Operations

Each client can request videos, receive streams from the local server, and save them locally.

📺 Scenarios Covered:
Scenario 1: Client 1 requests Video_2025.mp4, which is already cached in the local server. It is streamed directly to the client and saved.

Scenario 2: Client 2 requests Video_2024.mp4, which is not cached. The local server retrieves it from the global server, caches it, streams it to the client, and the client saves it.

Scenario 3: Client 3 requests a live video stream. The local server receives the live feed from the global server and relays it to the client in real time. The stream is also saved by the client.

---
This repository is maintained for educational purposes only, and plagiarism of the code may result in penalties.
