# ControlMouseWithCam.py
import os.path
import time
import pyautogui

class MouseController:
    def __init__(self):
        self.keypoints = [[] for _ in range(21)]  # Tạo danh sách 21 phần tử, tất cả là empty, example keypoints[1] = [12,23]
        self.signID = None
        self.old_kp5 = [0, 0] # old coord of keypoint 5
        self.sensitive = 3
        pyautogui.FAILSAFE = True

    def main(self):
        last_modified = 0
        while True:
            # Check if landmarks.txt has been updated
            try:
                current_modified = os.path.getmtime('landmarks.txt')
                if current_modified > last_modified:
                    self.update()
                    last_modified = current_modified
            except FileNotFoundError:
                pass
            if all(len(kp) == 2 for kp in self.keypoints) and self.signID is not None:
                # 4: moving, 1: close hand sign, 0: open hand sign
                if self.signID == 4:
                    self.moving(self.sensitive)
                elif self.signID == 1:
                    self.lift_mouse()
            time.sleep(0.033)

    def lift_mouse(self):
        self.old_kp5 = self.keypoints[5]

    def update(self):
        try:
            with open('landmarks.txt', 'r') as file:
                lines = file.readlines()
                if len(lines) < 22:
                    print("Insufficient data in landmarks.txt")
                    self.reset_state()
                    return

                new_keypoints = [[] for _ in range(21)]
                for i in range(21):
                    try:
                        coords = lines[i].split(':')[1].strip('[]\n').split(',')
                        if len(coords) != 2:
                            print(f"Invalid data format in line: {i}")
                            self.reset_state()
                            return
                        new_keypoints[i] = [int(coords[0]),int(coords[1])]
                    except (IndexError, ValueError) as e:
                        print(f"Error passing line: {i}: {e}")
                        self.reset_state()
                        return
                try:
                    self.signID = int(lines[21].strip())
                except ValueError:
                    print("Invalid sign ID format ")
                    self.reset_state()
                    return
                # Update keypoints and old_kp5 only if parsing succeeds
                self.keypoints = new_keypoints
        except FileNotFoundError:
            print("File landmarks.txt not found, waiting for app.py to write...")
            self.reset_state()
        except Exception as e:
            print(f"Error reading file: {e}")
            self.reset_state()

    def reset_state(self):
        """Reset keypoints and signID on error to avoid stale data."""
        self.keypoints = [[] for _ in range(21)]
        self.signID = None
        # self.old_kp5 = [0, 0]

    # method for moving mouse
    def moving(self, sensitivity):
        if len(self.keypoints[5]) != 2:
            return
        dist_x = (self.keypoints[5][0] - self.old_kp5[0])*sensitivity
        dist_y = (self.keypoints[5][1] - self.old_kp5[1])*sensitivity
        current_mouse_x, current_mouse_y = pyautogui.position()
        current_mouse_x = current_mouse_x + dist_x
        current_mouse_y = current_mouse_y + dist_y
        pyautogui.moveTo(current_mouse_x, current_mouse_y)
        self.old_kp5 = self.keypoints[5].copy()

    # method get screensize for control mouse
    def getScreenSize(self):
        return pyautogui.size()


if __name__ == "__main__":
    controller = MouseController()
    controller.main()