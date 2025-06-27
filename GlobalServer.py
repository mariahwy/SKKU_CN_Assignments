import socket
import threading
import os
import cv2
import numpy as np

PORT = 9000
BUFFER_SIZE = 1024
VIDEO_DIR = "video"

def handle_client(conn, addr):
    print(f"[Global Server] Connected to {addr}")
    try:
        request = conn.recv(100).decode().strip()
        print(f"[Global Server] Request: {request}")

        if request.lower() == "live":
            stream_live(conn)
        else:
            stream_recorded_video(request, conn)
    except Exception as e:
        print(f"[Global Server] Error handling client: {e}")
    finally:
        conn.close()
        print(f"[Global Server] Connection with {addr} closed")

def stream_recorded_video(filename, conn):
    filepath = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[Global Server] File not found: {filepath}")
        return

    print(f"[Global Server] Streaming recorded video: {filename}")
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                conn.sendall(chunk)
        print(f"[Global Server] Finished streaming file: {filename}")
    except Exception as e:
        print(f"[Global Server] Error streaming file: {e}")

    try:
        print(f"[Global Server] Launching viewer for: {filename}")
        os.system(f"python viewer_video.py {filepath} \"TRANSMITTING TO CACHE...\"")
    except Exception as e:
        print(f"[Global Server] Viewer launch error: {e}")

def stream_live(conn):
    print("[Global Server] Starting live stream from webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Global Server] Webcam failed to open.")
        return

    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[Global Server] Failed to read frame.")
                break

            # 프리뷰 표시
            preview = cv2.resize(frame, (480, 360))
            cv2.imshow("Global Server Live Preview", preview)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Global Server] Preview closed by user.")
                break

            # 전송 처리
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                print("[Global Server] JPEG encoding failed.")
                continue

            data = jpeg.tobytes()
            size = len(data)

            try:
                conn.sendall(size.to_bytes(4, byteorder='big'))
                conn.sendall(data)
                frame_count += 1
            except Exception as e:
                print(f"[Global Server] Send failed: {e}")
                break

    except Exception as e:
        print(f"[Global Server] Live stream error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[Global Server] Live stream ended.")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', PORT))
        server_socket.listen()
        print(f"[Global Server] Listening on port {PORT}...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
