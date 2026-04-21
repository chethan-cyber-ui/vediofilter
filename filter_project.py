import cv2
import numpy as np
import time

def gstreamer_pipeline(
    sensor_id=0, capture_width=1280, capture_height=720,
    display_width=640, display_height=360, 
    framerate=30, flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)
    )

def run_filters():
    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    filter_mode = '0'
    img_counter = 0 # To track number of saved images
    
    print("--- Jetson Nano Filter Studio ---")
    print("Controls: 0-9=Filters, s=Save Image, q=Quit")

    if not cap.isOpened():
        print("Error: Camera not found.")
        return

    sepia_kernel = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            key = cv2.waitKey(1) & 0xFF
            
            # --- INPUT HANDLING ---
            if key == ord('q'): 
                break
            elif key == ord('s'): # SAVE IMAGE LOGIC
                img_name = f"filter_capture_{img_counter}.jpg"
                # Note: We save 'processed' so the filter is included in the photo
                cv2.imwrite(img_name, processed)
                print(f"Screengrab saved as {img_name}")
                img_counter += 1
            elif ord('0') <= key <= ord('9'):
                filter_mode = chr(key)

            # --- FILTER LOGIC ---
            if filter_mode == '1': 
                processed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            elif filter_mode == '2': 
                processed = cv2.blur(frame, (10, 10))
            elif filter_mode == '3': 
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                processed = cv2.Canny(gray, 100, 200)
            elif filter_mode == '4': 
                processed = cv2.bitwise_not(frame)
            elif filter_mode == '5': 
                processed = cv2.transform(frame, sepia_kernel)
            elif filter_mode == '6': 
                processed = frame.copy()
                processed[:, :, [1, 2]] = 0 
            elif filter_mode == '7': 
                processed = frame.copy()
                processed[:, :, [0, 2]] = 0
            elif filter_mode == '8': 
                processed = frame.copy()
                processed[:, :, [0, 1]] = 0
            elif filter_mode == '9': 
                small = cv2.pyrDown(cv2.pyrDown(frame)) 
                for _ in range(2): small = cv2.medianBlur(small, 3)
                color = cv2.pyrUp(cv2.pyrUp(small))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, 1, 1, 9, 2)
                processed = cv2.bitwise_and(color, color, mask=edges)
            else:
                processed = frame

            # Show the filtered video
            cv2.imshow("Jetson Studio", processed)

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_filters()