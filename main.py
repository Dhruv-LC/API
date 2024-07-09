import cv2
import numpy as np
import mysql.connector
import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Initialize video capture
video_path = './highway_accident.mp4'
cap = cv2.VideoCapture(video_path)

# Function to extract license plate using EasyOCR
def extract_license_plate(frame):
    results = reader.readtext(frame)
    license_plate = ""
    for (bbox, text, prob) in results:
        # Here you might want to add more conditions to filter out text that doesn't look like a license plate
        if len(text) > 4:  # Simplified condition for demo purposes
            license_plate = text
            break
    return license_plate

# Connect to MySQL database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="iccc"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS incident (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_no VARCHAR(255),
        incident_location VARCHAR(255),
        lattitude VARCHAR(255),
        langtitude VARCHAR(255)
    )
''')
conn.commit()

# Main video processing loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    height, width, channels = frame.shape

    # Detect objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Extract incident-specific data
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Calculate ROI coordinates
                x, y = int(center_x - w / 2), int(center_y - h / 2)
                x_end, y_end = x + w, y + h

                # Ensure ROI coordinates are within frame boundaries
                if x < 0: x = 0
                if y < 0: y = 0
                if x_end > width: x_end = width
                if y_end > height: y_end = height

                # Crop the detected region for license plate extraction
                crop_img = frame[y:y_end, x:x_end]

                # Extract license plate
                vehicle_no = extract_license_plate(crop_img)
                incident_location = "Highway A"  # Example: Extract geo-location
                lattitude = 37.12345  # Example: Extract latitude
                langtitude = -122.54321  # Example: Extract longitude

                # Store in MySQL database
                insert_query = '''
                    INSERT INTO incident (vehicle_no, incident_location, lattitude, langtitude)
                    VALUES (%s, %s, %s, %s)
                '''
                insert_values = (vehicle_no, incident_location, lattitude, langtitude)
                cursor.execute(insert_query, insert_values)
                conn.commit()

                # Visualization on frame (similar to previous example)
                color = np.random.uniform(0, 255, size=(3,))
                label = str(classes[class_id])
                cv2.rectangle(frame, (x, y), (x_end, y_end), color, 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, vehicle_no, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display frame
    cv2.imshow('Video Capture', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
conn.close()
