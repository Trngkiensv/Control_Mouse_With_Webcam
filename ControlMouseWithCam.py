# ControlMouseWithCam.py
import time
import cv2 as cv
from keras.src.ops import switch

keypoints = [None] * 21  # Tạo danh sách 21 phần tử, tất cả là None
signID = None
def main():
    while True:
        this.signID = getSignID()

        if signID == 4:
            moving()
        elif signID == 5:

def moving():

    return None
# method update keypoints and signID
# id == 4: moving
def update():
    try:
        with open('landmarks.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) >= 22:
                id = int(lines[21])
        return id
    except FileNotFoundError:
        print("File landmarks.txt not found, waiting for app.py to write...")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def update_keypoints():
    global keypoints

if __name__ == "__main__":
    main()