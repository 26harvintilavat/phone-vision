""" 
clean_dataset.py

Removes images that do not contain a mobile phone using a pretrained YOLO model.

Usage:
    python src/clean_dataset.py
"""

from ultralytics import YOLO
import os

# Load pretrained YOLO model
model = YOLO("yolov8n.pt")

DATA_PATH = "data/raw"

VALID_EXT = (".jpg", ".jpeg", ".png", ".webp")

total_checked = 0
total_removed = 0

def clean_folder(folder_path):
    global total_checked, total_removed

    for img_name in os.listdir(folder_path):
        if not img_name.lower().endswith(VALID_EXT):
            continue

        img_path = os.path.join(folder_path, img_name)
        total_checked += 1

        try:
            results = model(img_path, verbose=False)
            boxes = results[0].boxes

            phone_detected = False

            if boxes is not None:
                for cls in boxes.cls:
                    # COCO class 67 = cell phone
                    if int(cls) == 67:
                        phone_detected = True
                        break
            
            if not phone_detected:
                os.remove(img_path)
                total_removed += 1

        except Exception as e:
            print(f"Error processing {img_name}: {e}")

def main():
    print("Starting dataset cleaning...")

    for folder in os.listdir(DATA_PATH):
        folder_path = os.path.join(DATA_PATH, folder)

        if os.path.isdir(folder_path):
            print(f"Cleaning: {folder}")
            clean_folder(folder_path)

    print("\nCleaning completed")
    print(f"Total checked: {total_checked}")
    print(f"Total removed: {total_removed}")

if __name__=="__main__":
    main()