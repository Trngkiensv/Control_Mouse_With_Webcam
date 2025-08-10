import multiprocessing
import tkinter as tk
from tkinter import ttk
from pygrabber.dshow_graph import FilterGraph
from PIL import Image, ImageTk
import cv2
from app import main as app_main
import logging
from ControlMouseWithCam import MouseController

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand To Mouse")
        self.root.geometry("1270x700")
        self.root.configure(bg="white")

        logging.basicConfig(filename='ui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Starting UI")
        # Queue cho giao tiếp
        self.queue = multiprocessing.Queue(maxsize=1000)
        self.camera_queue = multiprocessing.Queue(maxsize=1)

        # Font chữ
        self.label_font = ("Arial", 12, "bold")
        self.text_font = ("Arial", 10)
        self.button_font = ("Arial", 10, "bold")
        self.exit_font = ("Arial", 10, "bold")

        # Frame chính
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Frame cho video
        self.video_frame = tk.Frame(self.main_frame, bg="black")
        self.video_frame.grid(row=0, column=0, sticky="nsew")
        self.video_label = tk.Label(self.video_frame, bg="black", text="Camera Display Here", fg="white",
                                   font=self.text_font)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Frame điều khiển
        self.control_inner_frame = tk.Frame(self.main_frame, bd=1, relief="solid", bg="white",
                                           highlightbackground="gray", highlightthickness=3, padx=10, pady=10)
        self.control_inner_frame.grid(row=1, column=0, sticky="s")

        # Dropdown chọn camera
        tk.Label(self.control_inner_frame, text="Camera:", font=self.label_font, bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.camera_var = tk.StringVar(value="0")
        self.camera_combo = ttk.Combobox(self.control_inner_frame, textvariable=self.camera_var, width=25,
                                        state="readonly", font=self.text_font)
        self.camera_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.camera_combo.bind("<<ComboboxSelected>>", self.change_camera)
        self.update_camera_list()

        # Slider cho sensitivity
        tk.Label(self.control_inner_frame, text="Sensitivity:", font=self.label_font, bg="white").grid(row=0, column=2, padx=(0, 60), pady=5, sticky="w")
        self.sensitive_var = tk.DoubleVar(value=7.0)
        self.sensitive_slider = tk.Scale(self.control_inner_frame, from_=1.0, to=50.0, resolution=1.0,
                                        orient=tk.HORIZONTAL, variable=self.sensitive_var,
                                        command=self.update_sensitivity, length=150, font=self.text_font,
                                        bg="white", troughcolor="white")
        self.sensitive_slider.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Nút giảm độ nhạy
        self.decrease_btn = tk.Button(self.control_inner_frame, text="-", font=self.button_font, bg="white",
                                     relief="solid", bd=1, width=5, command=lambda: self.adjust_sensitivity(-1))
        self.decrease_btn.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="e")

        # Nút tăng độ nhạy
        self.increase_btn = tk.Button(self.control_inner_frame, text="+", font=self.button_font, bg="white",
                                     relief="solid", bd=1, width=5, command=lambda: self.adjust_sensitivity(1))
        self.increase_btn.grid(row=0, column=4, padx=(5, 0), pady=5, sticky="w")

        # Label cho hand sign
        self.sign_labels = {0: "Open Hand", 1: "Close Hand", 4: "Moving", 5: "Left Press",
                            6: "Right Press", 7: "Scroll Up", 8: "Scroll Down"}
        tk.Label(self.control_inner_frame, text="Hand Sign:", font=self.label_font, bg="white").grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.sign_var = tk.StringVar(value="No Sign")
        tk.Label(self.control_inner_frame, textvariable=self.sign_var, font=self.text_font, bg="white").grid(row=0, column=6, padx=(0, 20), pady=5, sticky="w")

        # Nút thoát
        self.exit_btn = tk.Button(self.control_inner_frame, text="Exit", command=self.exit_app, font=self.exit_font,
                                 width=12, bg="red", fg="white", relief="solid", bd=1)
        self.exit_btn.grid(row=0, column=7, pady=5, sticky="e")

        # Cấu hình grid
        self.main_frame.grid_rowconfigure(0, weight=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.control_inner_frame.grid_columnconfigure(7, weight=1)

        # Khởi động tiến trình
        self.app_process = multiprocessing.Process(target=app_main, args=(self.queue, self.camera_queue))
        # Sửa đổi: Tạo instance MouseController trước và truyền hàm main
        mouse_controller = MouseController(self.queue, self.sensitive_var)
        self.mouse_process = multiprocessing.Process(target=mouse_controller.main)
        self.app_process.start()
        self.mouse_process.start()

        # Cập nhật video và hand sign
        self.update_video()

        # Cập nhật video và hand sign
        self.update_video()

    def update_camera_list(self):
        camera_list = []
        try:
            graph = FilterGraph()
            devices = graph.get_input_devices()
            for i, device in enumerate(devices):
                camera_list.append((str(i), device))
            logging.info(f"Found cameras: {devices}")
        except Exception as e:
            logging.error(f"Error accessing cameras: {e}")
            camera_list = [("0", "No Camera")]

        if camera_list:
            self.camera_combo['values'] = [name for _, name in camera_list]
            self.camera_ids = {name: id for id, name in camera_list}
            self.camera_var.set(camera_list[0][1])
        else:
            self.camera_combo['values'] = ["No Camera"]
            self.camera_var.set("No Camera")
            self.camera_ids = {"No Camera": "0"}

    def change_camera(self, event):
        selected_camera = self.camera_var.get()
        camera_id = self.camera_ids.get(selected_camera, "0")
        try:
            self.camera_queue.put_nowait(camera_id)
            logging.info(f"Sent camera ID: {camera_id} ({selected_camera})")  # Sửa đổi: Thay print bằng logging
        except multiprocessing.queues.Full:
            logging.warning("Camera queue full, skipping")  # Sửa đổi: Thay print bằng logging

    def update_sensitivity(self, value):
        logging.info(f"Sensitivity: {self.sensitive_var.get()}")

    def adjust_sensitivity(self, delta):
        current = self.sensitive_var.get()
        new_value = max(1.0, min(50.0, current + delta))
        self.sensitive_var.set(new_value)
        logging.info(f"Sensitivity adjusted to: {new_value}")

    def update_video(self):
        try:
            landmark_list, hand_sign_id, frame = self.queue.get_nowait()
            if frame is not None and frame.size > 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                frame_width = self.video_frame.winfo_width()
                frame_height = self.video_frame.winfo_height()
                if frame_width > 1 and frame_height > 1:
                    img = img.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((960, 540), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            if hand_sign_id is not None:
                self.sign_var.set(self.sign_labels.get(hand_sign_id, "Unknown"))
                logging.info(f"Updated hand sign: {self.sign_var.get()}")
        except multiprocessing.queues.Empty:
            pass
        except Exception as e:
            logging.error(f"Error updating video: {e}")
        self.root.after(20, self.update_video)

    def exit_app(self):
        try:
            # Sửa đổi: Xóa queue trước khi thoát
            while not self.queue.empty():
                self.queue.get_nowait()
            while not self.camera_queue.empty():
                self.camera_queue.get_nowait()
            logging.info("Cleared queues")  # Sửa đổi: Thêm log
        except multiprocessing.queues.Empty:
            pass
        self.app_process.terminate()
        self.mouse_process.terminate()
        logging.info("Terminated processes")  # Sửa đổi: Thêm log
        self.root.quit()
        logging.info("UI closed")  # Sửa đổi: Thêm log

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()