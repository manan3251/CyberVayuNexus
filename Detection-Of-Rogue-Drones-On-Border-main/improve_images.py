import cv2
import numpy as np
from pathlib import Path
import os

def enhance_image(img):
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    # Merge channels
    limg = cv2.merge((cl,a,b))
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # Apply sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return sharpened

def main():
    # Set paths
    bad_dir = Path('train_dataset/content/train_dataset/images/bad')
    improved_dir = Path('train_dataset/content/train_dataset/images/improved')
    improved_dir.mkdir(exist_ok=True)
    
    # Process each bad image
    for img_path in bad_dir.glob('*.jpg'):
        # Read image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Failed to read {img_path.name}")
            continue
        
        # Enhance image
        enhanced = enhance_image(img)
        
        # Save enhanced image
        output_path = improved_dir / img_path.name
        cv2.imwrite(str(output_path), enhanced)
        print(f"Enhanced {img_path.name}")
        
        # Copy corresponding label file if it exists
        label_path = Path(str(img_path).replace('images', 'labels').replace('.jpg', '.txt'))
        if label_path.exists():
            new_label_path = Path(str(output_path).replace('images', 'labels').replace('.jpg', '.txt'))
            os.makedirs(new_label_path.parent, exist_ok=True)
            os.system(f'copy "{label_path}" "{new_label_path}"')

if __name__ == "__main__":
    main() 