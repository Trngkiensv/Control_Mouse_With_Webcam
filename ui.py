import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import multiprocessing
import cv2


class AppUI:
    def __init__(self, root, queue, camera_queue, app_process):
        self.root = root
        self.root.title("Hand To Mouse")
        self.root.geometry("1270x700")
        self.root.configure(bg="white")
        self.queue = queue
        self.camera_queue = camera_queue
        self.app_process = app_process
        self.camera_ids = {}

        # Font chữ
        self.label_font = ("Arial", 12, "bold")
        self.text_font = ("Arial", 10)
        self.exit_font = ("Arial", 10, "bold")
        self.button_font = ("Arial", 10, "bold")

        # Frame chính
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Frame cho video
        self.video_frame = tk.Frame(self.main_frame, bg="black")
        self.video_frame.grid(row=0, column=0, sticky="nsew")
        self.video_label = tk.Label(self.video_frame, bg="black", text="Camera Display Here", fg="white",
                                    font=self.text_font)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Frame điều khiển với viền mỏng và padding, căn sát dưới
        self.control_inner_frame = tk.Frame(self.main_frame, bd=1, relief="solid", bg="white",
                                            highlightbackground="gray", highlightthickness=3, padx=10, pady=10)
        self.control_inner_frame.grid(row=1, column=0, sticky="s")

        # Dropdown chọn camera
        tk.Label(self.control_inner_frame, text="Camera:", font=self.label_font, bg="white").grid(row=0, column=0,
                                                                                                  padx=5, pady=5,
                                                                                                  sticky="w")
        self.camera_var = tk.StringVar(value="0")
        self.camera_combo = ttk.Combobox(self.control_inner_frame, textvariable=self.camera_var, width=25,
                                         state="readonly", font=self.text_font)
        self.camera_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.camera_combo.bind("<<ComboboxSelected>>", self.change_camera)
        self.update_camera_list()

        # Slider cho sensitivity với bước nhảy 1
        tk.Label(self.control_inner_frame, text="Sensitivity:", font=self.label_font, bg="white").grid(row=0, column=2,
                                                                                                       padx=(0, 60),
                                                                                                       pady=5,
                                                                                                       sticky="w")
        self.sensitive_var = tk.DoubleVar(value=7.0)
        self.sensitive_slider = tk.Scale(self.control_inner_frame, from_=1.0, to=50.0, resolution=1.0,
                                         orient=tk.HORIZONTAL, variable=self.sensitive_var, length=150,
                                         font=self.text_font,
                                         bg="white", troughcolor="white")
        self.sensitive_slider.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Nút giảm độ nhạy (bên trái thanh trượt) với viền đen, to ra theo chiều ngang
        self.decrease_btn = tk.Button(self.control_inner_frame, text="-", font=self.button_font, bg="white",
                                      relief="solid", bd=1, width=5,
                                      )
        self.decrease_btn.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="e")

        self.increase_btn = tk.Button(self.control_inner_frame, text="+", font=self.button_font, bg="white",
                                      relief="solid", bd=1, width=5,
                                      )
        self.increase_btn.grid(row=0, column=4, padx=(5, 0), pady=5, sticky="w")

        # Label cho hand sign
        tk.Label(self.control_inner_frame, text="Hand Sign:", font=self.label_font, bg="white").grid(row=0, column=5,
                                                                                                     padx=5, pady=5,
                                                                                                     sticky="w")
        self.sign_var = tk.StringVar(value="No Sign")
        tk.Label(self.control_inner_frame, textvariable=self.sign_var, font=self.text_font, bg="white").grid(row=0,
                                                                                                             column=6,
                                                                                                             padx=(0,
                                                                                                                   20),
                                                                                                             pady=5,
                                                                                                             sticky="w")

        # Nút thoát với màu đỏ và chữ trắng đậm, viền đen
        self.exit_btn = tk.Button(self.control_inner_frame, text="Exit", command=self.exit_app, font=self.exit_font,
                                  width=12, bg="red", fg="white", relief="solid", bd=1)
        self.exit_btn.grid(row=0, column=7, pady=5, sticky="e")

        # Cấu hình grid
        self.main_frame.grid_rowconfigure(0, weight=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.control_inner_frame.grid_columnconfigure(7, weight=1)

        self.update_video()

    def change_camera(self, event):
        selected_camera = self.camera_var.get()
        camera_id = self.camera_ids.get(selected_camera, 0)
        try:
            self.camera_queue.put_nowait(camera_id)
        except multiprocessing.queues.Full:
            print("Camera queue full, skipping send")

    def update_camera_list(self):
        camera_list = []
        try:
            for index in range(20):
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    camera_list.append((index, f"Camera {index}"))
                cap.release()
        except Exception as e:
            print(f"Error accessing cameras: {e}")
        if not camera_list:
            camera_list = [(0, "No Camera")]
        self.camera_combo['values'] = [name for _, name in camera_list]
        self.camera_ids = {name: id for id, name in camera_list}
        print(self.camera_ids)
        if camera_list:
            self.camera_var.set(camera_list[0][1])
        else:
            self.camera_var.set("No Camera")
            self.camera_combo['values'] = ["No Camera"]

    def update_video(self):
        try:
            # Lấy dữ liệu từ queue
            _, _, frame = self.queue.get_nowait()  # Bỏ qua landmark_list và hand_sign_id
            if frame is not None:
                # Chuyển đổi frame từ OpenCV (BGR) sang RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Chuyển đổi sang định dạng Tkinter
                img = Image.fromarray(frame_rgb)
                # Điều chỉnh kích thước
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk  # Giữ tham chiếu
                self.video_label.configure(image=imgtk)
        except multiprocessing.queues.Empty:
            pass  # Không có frame mới
        except Exception as e:
            print(f"Error displaying video: {e}")
        # Lặp lại mỗi 1ms
        self.root.after(1, self.update_video)

    def exit_app(self):
        try:
            self.camera_queue.put_nowait("exit")
        except multiprocessing.queues.Full:
            pass
        self.app_process.terminate()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    queue = multiprocessing.Queue(maxsize=1000)
    camera_queue = multiprocessing.Queue(maxsize=10)
    app = AppUI(root, queue, camera_queue)
    root.mainloop()
