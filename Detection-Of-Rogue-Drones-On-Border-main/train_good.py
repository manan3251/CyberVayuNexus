import torch
import os
from pathlib import Path

def main():
    # Set paths
    data_yaml = 'train_dataset/content/train_dataset/data.yaml'
    weights = 'yolov5s.pt'
    
    # Training parameters
    img_size = 640
    batch_size = 16
    epochs = 100
    
    # Training command
    cmd = f'python yolov5/train.py --img {img_size} --batch {batch_size} --epochs {epochs} --data {data_yaml} --weights {weights} --cache'
    
    print("Starting training with good images...")
    os.system(cmd)

if __name__ == "__main__":
    main() 