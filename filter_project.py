import cv2

# 1. GStreamer Pipeline for Jetson Nano (CSI Camera)
def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

# 2. Initialize Camera
print("Initializing CSI Camera...")
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

filter_mode = '0'
print("Controls: 1=Grayscale, 2=Blur, 3=Sketch, 4=Inverted, 0=Normal, q=Quit")

if cap.isOpened():
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 3. Listen for Keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key in [ord('0'), ord('1'), ord('2'), ord('3'), ord('4')]:
                filter_mode = chr(key)

            # 4. Apply Filters
            if filter_mode == '1':
                # Grayscale
                processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            elif filter_mode == '2':
                # Blur
                processed_frame = cv2.GaussianBlur(frame, (15, 15), 0)
                
            elif filter_mode == '3':
                # Sketch (Edge Detection)
                temp_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                processed_frame = cv2.Canny(temp_gray, 50, 150)
                
            elif filter_mode == '4':
                # Invert (Negative)
                processed_frame = cv2.bitwise_not(frame)
                
            else:
                # Normal
                processed_frame = frame

            # 5. Display Result
            cv2.imshow('Jetson Nano Filter Proj', processed_frame)

    finally:
        # 6. Proper Cleanup (Crucial for Jetson)
        cap.release()
        cv2.destroyAllWindows()
else:
    print("Error: Unable to open camera. Check ribbon cable connection.")
