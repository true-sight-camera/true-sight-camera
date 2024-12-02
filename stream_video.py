import cv2 as cv

# Open the default camera (camera index 0)
cap = cv.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if frame is captured correctly
    if not ret:
        print("Error: Could not read frame.")
        break

    # Display the frame
    cv.imshow("Camera Feed", frame)

    # Press 'q' to exit the loop
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv.destroyAllWindows()
