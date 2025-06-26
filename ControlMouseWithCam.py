# ControlMouseWithCam.py
import os.path
import time
import pyautogui
import keyboard

class MouseController:
    def __init__(self):
        self.keypoints = [[] for _ in range(21)]  # Tạo danh sách 21 phần tử, tất cả là empty, example keypoints[1] = [12,23]
        self.signID = None
        self.old_kp_moving_point = [0, 0] # old coord of keypoint 0
        self.sensitive = 3
        self.moving_point = 0
        self.last_mouse_x , self.last_mouse_y = pyautogui.position()
        self.is_left_pressed = False
        pyautogui.FAILSAFE = True


    def main(self):
        last_modified = 0
        while True:
            # runtime sensitivity adjustment
            if keyboard.is_pressed('+'):
                self.sensitive += 0.5
                print(f"Sensitivity: {self.sensitive}")
            if keyboard.is_pressed('-'):
                self.sensitive = max(0.5, self.sensitive - 0.5)
                print(f"Sensitivity: {self.sensitive}")
            if keyboard.is_pressed('ctrl+shift+b'):
                break
            # Check if landmarks.txt has been updated
            try:
                current_modified = os.path.getmtime('landmarks.txt')
                if self.signID is None:
                    if current_modified > last_modified:
                        self.update()
                        last_modified = current_modified
                        self.signID = 4 # force signID to move sign when first read
                else:
                    if current_modified > last_modified:
                        self.update()
                        last_modified = current_modified
            except FileNotFoundError:
                pass
            if all(len(kp) == 2 for kp in self.keypoints) and self.signID is not None:
                # 4: moving, 1: close hand sign, 0: open hand sign, 5: left mouse press
                if self.signID == 4:
                    if self.is_left_pressed:
                        self.left_release()
                        self.is_left_pressed = False
                    self.moving(self.sensitive)
                elif self.signID == 1:
                    self.reset_mouse_reference()
                elif self.signID == 5:
                    if not self.is_left_pressed:
                        self.left_press()
                        self.is_left_pressed = True
                        self.moving(self.sensitive)
                    else:
                        self.moving(self.sensitive)
            time.sleep(0.033)

    def reset_mouse_reference(self):
        if len(self.keypoints[self.moving_point]) == 2:
            self.old_kp_moving_point = self.keypoints[self.moving_point].copy()
        else:
            print("Invalid keypoint data, skipping reset")

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

    # method for moving mouse
    def moving(self, sensitivity):
        if len(self.keypoints[self.moving_point]) != 2:
            return
        # Calculate displacement
        dist_x = (self.keypoints[self.moving_point][0] - self.old_kp_moving_point[0]) * sensitivity
        dist_y = (self.keypoints[self.moving_point][1] - self.old_kp_moving_point[1]) * sensitivity
        current_mouse_x, current_mouse_y = pyautogui.position()
        # if self.last_mouse_x is None:
        #     self.last_mouse_x, self.last_mouse_y = current_mouse_x, current_mouse_y

        new_x = 0.3 * (current_mouse_x + dist_x) + 0.7 * self.last_mouse_x
        new_y = 0.3 * (current_mouse_y + dist_y) + 0.7 * self.last_mouse_y
        self.last_mouse_x, self.last_mouse_y = new_x, new_y
        # Clamp to screen bounds
        screen_width, screen_height = self.getScreenSize()
        new_x = max(0, min(new_x, screen_width - 1))
        new_y = max(0, min(new_y, screen_height - 1))
        pyautogui.moveTo(new_x, new_y, duration=0.033, tween=pyautogui.easeInOutQuad)
        self.old_kp_moving_point = self.keypoints[self.moving_point].copy()

    def left_press(self):
        current_mouse_x, current_mouse_y = pyautogui.position()
        pyautogui.mouseDown(current_mouse_x, current_mouse_y, button='left')


    def left_release(self):
        current_mouse_x, current_mouse_y = pyautogui.position()
        pyautogui.mouseUp(current_mouse_x, current_mouse_y, button='left')

    # method get screensize for control mouse
    def getScreenSize(self):
        return pyautogui.size()


if __name__ == "__main__":
    controller = MouseController()
    controller.main()