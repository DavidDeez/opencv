import cv2
import numpy as np

def annotate_ui_elements(image_path, output_path):
    """
    Reads a screenshot, detects UI elements (buttons, inputs), 
    draws numbered bounding boxes over them, and returns their coordinates.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
    
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Canny Edge Detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Dilate edges slightly to close gaps in UI borders
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    ui_elements = []
    element_id = 1
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        
        # Filter out tiny noise and massive containers (like the whole screen)
        if 500 < area < (img.shape[0] * img.shape[1] * 0.8):
            # Check aspect ratio to avoid weirdly shaped noise
            aspect_ratio = float(w)/h
            
            ui_elements.append({
                "id": element_id,
                "x": x, "y": y, "w": w, "h": h
            })
            
            # Draw green bounding box
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw ID label background
            label_bg_pt1 = (x, y - 20) if y - 20 > 0 else (x, y)
            label_bg_pt2 = (x + 25, y) if y - 20 > 0 else (x + 25, y + 20)
            cv2.rectangle(img, label_bg_pt1, label_bg_pt2, (0, 255, 0), -1)
            
            # Put ID text
            text_pos = (x + 2, y - 5 if y - 20 > 0 else y + 15)
            cv2.putText(img, str(element_id), text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            element_id += 1
            
    cv2.imwrite(output_path, img)
    return ui_elements

if __name__ == "__main__":
    print("Vision module loaded. Ready to process screenshots.")
