import cv2
import numpy as np

def annotate_ui_elements(image_path, output_path, canny_low=50, canny_high=150):
    """
    Reads a screenshot, detects UI elements, and draws numbered bounding boxes.
    Now supports dynamic tuning of Canny edge detection thresholds.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Dynamic Canny Edge Detection (Agent can tune these!)
    edges = cv2.Canny(gray, canny_low, canny_high)
    
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    ui_elements = []
    element_id = 1
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        
        if 500 < area < (img.shape[0] * img.shape[1] * 0.8):
            ui_elements.append({
                "id": element_id,
                "x": x, "y": y, "w": w, "h": h
            })
            
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            label_bg_pt1 = (x, y - 20) if y - 20 > 0 else (x, y)
            label_bg_pt2 = (x + 25, y) if y - 20 > 0 else (x + 25, y + 20)
            cv2.rectangle(img, label_bg_pt1, label_bg_pt2, (0, 255, 0), -1)
            
            text_pos = (x + 2, y - 5 if y - 20 > 0 else y + 15)
            cv2.putText(img, str(element_id), text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            element_id += 1
            
    cv2.imwrite(output_path, img)
    return ui_elements
