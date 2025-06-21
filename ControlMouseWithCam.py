# ControlMouseWithCam.py
import time

import pyautogui

keypoints = [[] for _ in range(21)]  # Tạo danh sách 21 phần tử, tất cả là empty, example keypoints[1] = [12,23]
signID = None
movingpoint = None # point use to determine if moving
def main():
    while True:
        update()
        if all(len(kp) == 2 for kp in keypoints) and signID is not None:
            if signID == 4:
                moving()
        time.sleep(0.01)

# method for moving mouse
def moving():
    return None

# method get screensize for control mouse
def getScreenSize():
    return pyautogui.size()

# method update keypoints and signID
# id == 4: moving
def update():
    global keypoints, signID
    try:
        with open('landmarks.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) < 22:
                print("Insufficient data in landmarks.txt")
                return
            for i in range(21):
                coords = lines[i].split(':')[1].strip('[]\n').split(',')
                if len(coords) == 2:
                    keypoints[i] = coords
                else:
                    print(f"Invalid data format in line: {i}")
                    return
            try:
                signID = int(lines[21].strip())
            except ValueError:
                print("Invalid sign ID format ")
    except FileNotFoundError:
        print("File landmarks.txt not found, waiting for app.py to write...")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    main()