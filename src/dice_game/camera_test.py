import cv2

# 3번 카메라 연결
cap = cv2.VideoCapture(3)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    cv2.imshow('Camera Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): # 'q' 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
