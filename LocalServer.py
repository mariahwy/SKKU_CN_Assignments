import socket
import threading
import os
import cv2
import numpy as np

LOCAL_PORT = 8000
GLOBAL_SERVER_ADDR = ('127.0.0.1', 9000)
BUFFER_SIZE = 1024
CACHE_DIR = "./cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def preview_video(filepath):
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        print("[Local Server] Cannot open video for preview:", filepath)
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (480, 360))
        cv2.imshow("SENDING TO CLIENT...", resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def stream_file_to_client(client_socket, filepath):
    try:
        print("[Local Server] Sending cached file to client:", filepath)
        threading.Thread(target=preview_video, args=(filepath,), daemon=True).start()

        with open(filepath, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.sendall(data)
        print("[Local Server] Finished sending file.")
    except Exception as e:
        print("[Local Server] File streaming error:", e)
    finally:
        client_socket.close()

def fetch_from_global(video_name):
    print("[Local Server] Fetching file from Global Server:", video_name)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as global_sock:
        global_sock.connect(GLOBAL_SERVER_ADDR)
        global_sock.sendall(video_name.encode())

        cache_path = os.path.join(CACHE_DIR, video_name)
        with open(cache_path, 'wb') as f:
            while True:
                data = global_sock.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
    print("[Local Server] File fetched and cached:", cache_path)
    return cache_path

def relay_live_stream(client_socket):
    print("[Local Server] Starting live stream relay")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as global_sock:
        global_sock.connect(GLOBAL_SERVER_ADDR)
        global_sock.sendall(b"live")
        print("[Local Server] Connected to Global Server for live stream")

        try:
            while True:
                header = recv_exact(global_sock, 4)
                if not header:
                    print("[Local Server] Failed to receive frame header")
                    break
                frame_size = int.from_bytes(header, byteorder='big')
                frame_data = recv_exact(global_sock, frame_size)
                if not frame_data:
                    print("[Local Server] Failed to receive frame data")
                    break

                # 미리보기용 디코딩
                np_arr = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is not None:
                    resized = cv2.resize(frame, (480, 360))
                    cv2.imshow("Local Server Live Preview", resized)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("[Local Server] Preview manually closed.")
                        break

                # 클라이언트로 전송
                try:
                    client_socket.sendall(header + frame_data)
                except Exception as e:
                    print("[Local Server] Error sending to client:", e)
                    break

        except Exception as e:
            print("[Local Server] Relay error:", e)

    cv2.destroyAllWindows()
    print("[Local Server] Live stream relay finished")
    client_socket.close()

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_client(client_socket):
    try:
        video_name = client_socket.recv(1024).decode().strip()
        print("[Local Server] Client requested:", video_name)

        if video_name == "live":
            relay_live_stream(client_socket)
            return

        cached_path = os.path.join(CACHE_DIR, video_name)
        if not os.path.exists(cached_path):
            print("[Local Server] Cache miss. Fetching...")
            cached_path = fetch_from_global(video_name)
        else:
            print("[Local Server] Cache hit. Using local copy.")

        stream_file_to_client(client_socket, cached_path)
    except Exception as e:
        print("[Local Server] Error handling client:", e)
    finally:
        client_socket.close()

def run_local_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(('127.0.0.1', LOCAL_PORT))
        server_sock.listen(5)
        print(f"[Local Server] Listening on port {LOCAL_PORT}...")

        while True:
            client_sock, addr = server_sock.accept()
            print("[Local Server] Accepted connection from", addr)
            threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    run_local_server()
