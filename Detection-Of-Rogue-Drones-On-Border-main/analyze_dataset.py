import cv2
import torch
import numpy as np
from pathlib import Path
import os

# Initialize YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.conf = 0.3  # Confidence threshold
model.iou = 0.45  # IOU threshold

def analyze_image(image_path, label_path):
    # Read image
    img = cv2.imread(str(image_path))
    if img is None:
        return False, "Failed to read image"
    
    # Make detection
    results = model(img)
    detections = results.xyxy[0].cpu().numpy()
    
    # Read ground truth label
    try:
        with open(label_path, 'r') as f:
            gt_labels = f.readlines()
    except:
        return False, "Failed to read label file"
    
    # Check if we have any detections
    if len(detections) == 0:
        return False, "No detections"
    
    # Check if we have high confidence detections
    high_conf_detections = [d for d in detections if d[4] > 0.5]
    if len(high_conf_detections) == 0:
        return False, "No high confidence detections"
    
    return True, "Good detection"

def main():
    # Paths
    images_dir = Path('train_dataset/content/train_dataset/images/val')
    labels_dir = Path('train_dataset/content/train_dataset/labels/val')
    
    # Create directories for good and bad images
    good_dir = Path('train_dataset/content/train_dataset/images/good')
    bad_dir = Path('train_dataset/content/train_dataset/images/bad')
    good_dir.mkdir(exist_ok=True)
    bad_dir.mkdir(exist_ok=True)
    
    # Analyze each image
    for img_path in images_dir.glob('*.jpg'):
        label_path = labels_dir / f"{img_path.stem}.txt"
        
        if not label_path.exists():
            print(f"Moving {img_path.name} to bad directory - No label file")
            os.rename(str(img_path), str(bad_dir / img_path.name))
            continue
        
        is_good, reason = analyze_image(img_path, label_path)
        
        if is_good:
            print(f"Moving {img_path.name} to good directory")
            os.rename(str(img_path), str(good_dir / img_path.name))
        else:
            print(f"Moving {img_path.name} to bad directory - {reason}")
            os.rename(str(img_path), str(bad_dir / img_path.name))

if __name__ == "__main__":
    main() 