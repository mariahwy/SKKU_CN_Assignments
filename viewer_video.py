import sys
import cv2

video_path = sys.argv[1]
window_title = sys.argv[2] if len(sys.argv) > 2 else "Video Preview"

cap = cv2.VideoCapture(video_path)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    resized = cv2.resize(frame, (480, 360))  # 원하는 크기로 줄이기
    cv2.imshow(window_title, resized)        # 이 줄 수정!
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
