# ControlMouseWithCam.py
import time
import pyautogui
import keyboard
import multiprocessing
from pynput.mouse import Controller, Button

class MouseController:
    def __init__(self, queue):
        self.keypoints = [[] for _ in range(21)]  # Tạo danh sách 21 phần tử, tất cả là empty, example keypoints[1] = [12,23]
        self.signID = None
        self.old_kp_moving_point = [0, 0] # old coord of keypoint 0
        self.sensitive = 7
        self.moving_point = 0
        self.queue = queue
        self.last_mouse_x, self.last_mouse_y = pyautogui.position()
        self.is_left_pressed = False
        self.is_right_pressed = False
        pyautogui.FAILSAFE = True
        self.mouse = Controller()
        self.first_update = True
        self.count_to_scroll = 0
        self.last_scroll_direction = ""
        self.scroll_count = 0

    def main(self):
        while True:
            # Update from queue
            self.update()
            if self.signID is not None:
                # 4: moving, 1: close hand sign, 0: open hand sign, 5: left mouse press
                if self.signID == 4:
                    if self.is_left_pressed:
                        self.left_release()
                        self.is_left_pressed = False
                    if self.is_right_pressed:
                        self.right_release()
                        self.is_right_pressed = False
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
                elif self.signID == 6:
                    if not self.is_right_pressed:
                        self.right_press()
                        self.is_right_pressed = True
                        self.moving(self.sensitive)
                    else:
                        self.moving(self.sensitive)
                elif self.signID == 7:
                    if self.is_left_pressed or self.is_right_pressed:
                        self.left_release()
                        self.is_left_pressed = False
                        self.right_press()
                        self.is_right_pressed = False
                    self.scroll_up()
                elif self.signID == 8:
                    if self.is_left_pressed or self.is_right_pressed:
                        self.left_release()
                        self.is_left_pressed = False
                        self.right_press()
                        self.is_right_pressed = False
                    self.scroll_down()
                print(f"hand_sign_id: {self.signID}")
            time.sleep(0.005)

    def reset_mouse_reference(self):
        if len(self.keypoints[self.moving_point]) == 2:
            self.old_kp_moving_point = self.keypoints[self.moving_point].copy()
        else:
            print("Invalid keypoint data, skipping reset")
        self.scroll_count = 0
        self.last_scroll_direction = ""
        self.count_to_scroll = 0

    def update(self):
        try:
            landmark_list, hand_sign_id = self.queue.get_nowait()
            if landmark_list is not None and hand_sign_id is not None:
                if len(landmark_list) == 21 and all(len(coord) == 2 for coord in landmark_list):
                    self.keypoints = [[int(x), int(y)] for x, y in landmark_list]
                    self.signID = int(hand_sign_id)
                    if self.first_update:
                        self.signID = 4  # Force signID to moving on first valid read
                        self.first_update = False
                else:
                    print("Invalid landmark data, skipping update")
                    self.reset_state()
            elif landmark_list is None and hand_sign_id is None:
                print("No landmark data, skipping update")
                self.reset_state()
        except multiprocessing.queues.Empty:
            pass
        except (ValueError, TypeError) as e:
            print(f"Error processing queue data: {e}")
            self.reset_state()

    def reset_state(self):
        """Reset keypoints and signID on error to avoid stale data."""
        self.keypoints = [[] for _ in range(21)]
        self.signID = None


    # method for moving mouse
    def moving(self, sensitivity):
        # Calculate displacement
        dist_x = (self.keypoints[self.moving_point][0] - self.old_kp_moving_point[0]) * sensitivity
        dist_y = (self.keypoints[self.moving_point][1] - self.old_kp_moving_point[1]) * sensitivity
        current_mouse_x, current_mouse_y = self.mouse.position
        new_x = 0.3 * (current_mouse_x + dist_x) + 0.7 * self.last_mouse_x
        new_y = 0.3 * (current_mouse_y + dist_y) + 0.7 * self.last_mouse_y
        self.last_mouse_x, self.last_mouse_y = new_x, new_y
        # Clamp to screen bounds
        screen_width, screen_height = pyautogui.size()
        new_x = max(0, min(new_x, screen_width - 1))
        new_y = max(0, min(new_y, screen_height - 1))
        # pyautogui.moveTo(new_x, new_y, duration=0.0, tween=pyautogui.easeInOutQuad)
        self.mouse.position = (new_x, new_y)
        self.old_kp_moving_point = self.keypoints[self.moving_point].copy()

    def left_press(self):
        self.mouse.press(Button.left)


    def left_release(self):
        self.mouse.release(Button.left)

    def right_press(self):
        self.mouse.press(Button.right)


    def right_release(self):
        self.mouse.release(Button.right)

    # method get screensize for control mouse
    def getScreenSize(self):
        return pyautogui.size()

    def scroll_up(self):  # Lăn chuột len
        if self.count_to_scroll >= 20:
            self.mouse.scroll(0, 1)
            self.scroll_count += 1
            self.count_to_scroll = 0
            self.adjust_count_to_scroll("up")
        else:
            self.adjust_count_to_scroll("up")

    def scroll_down(self):
        if self.count_to_scroll >= 20:
            self.mouse.scroll(0, -1)
            self.scroll_count += 1
            self.count_to_scroll = 0
            self.adjust_count_to_scroll("down")
        else:
            self.adjust_count_to_scroll("down")

    def adjust_count_to_scroll(self, direction):
        if direction == self.last_scroll_direction:
            self.count_to_scroll += 1
        else:
            self.last_scroll_direction = direction
            self.scroll_count = 0
            self.count_to_scroll = 0
        if self.scroll_count >= 5:
            self.count_to_scroll = max(15, self.count_to_scroll)

if __name__ == "__main__":
    controller = MouseController()
    controller.main()