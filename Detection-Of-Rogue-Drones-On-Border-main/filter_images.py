import cv2
import torch
import shutil
from pathlib import Path

def setup_directories():
    # Create directories if they don't exist
    base_dir = Path("train_dataset/content/train_dataset/images")
    detected_dir = base_dir / "detected"
    undetected_dir = base_dir / "undetected"
    
    detected_dir.mkdir(exist_ok=True)
    undetected_dir.mkdir(exist_ok=True)
    
    return base_dir, detected_dir, undetected_dir

def main():
    print("Initializing YOLOv5 model...")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5m')
    model.conf = 0.4  # Confidence threshold
    model.iou = 0.45  # IOU threshold
    
    # Setup directories
    base_dir, detected_dir, undetected_dir = setup_directories()
    train_dir = base_dir / "train"
    
    # Get all images
    image_files = sorted([f for f in train_dir.glob("*.jpg") if f.is_file()])
    total_images = len(image_files)
    print(f"Found {total_images} images to process")
    
    detected_count = 0
    undetected_count = 0
    
    for idx, img_path in enumerate(image_files, 1):
        print(f"Processing image {idx}/{total_images}: {img_path.name}")
        
        # Read image
        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"Failed to load image: {img_path}")
            continue
        
        # Make detections
        results = model(frame)
        
        # Check for drone detections
        drone_detected = False
        for *box, conf, cls in results.xyxy[0]:
            cls = int(cls)
            conf = float(conf)
            
            if cls == 4:  # Drone/Airplane class
                # Calculate aspect ratio
                x1, y1, x2, y2 = map(int, box)
                box_width = x2 - x1
                box_height = y2 - y1
                aspect_ratio = box_width / box_height if box_height != 0 else 0
                
                # Check if detection meets our criteria
                if 0.25 <= aspect_ratio <= 4 and conf >= 0.45:
                    drone_detected = True
                    break
        
        # Move the image to appropriate directory
        if drone_detected:
            shutil.copy2(img_path, detected_dir / img_path.name)
            detected_count += 1
            print(f"✓ Drone detected in {img_path.name}")
        else:
            shutil.copy2(img_path, undetected_dir / img_path.name)
            undetected_count += 1
            print(f"✗ No drone detected in {img_path.name}")
    
    print("\nProcessing complete!")
    print(f"Total images processed: {total_images}")
    print(f"Images with drones detected: {detected_count}")
    print(f"Images with no drones detected: {undetected_count}")
    print(f"\nDetected images moved to: {detected_dir}")
    print(f"Undetected images moved to: {undetected_dir}")

if __name__ == "__main__":
    main() 