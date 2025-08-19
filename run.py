import multiprocessing as mp
import tkinter as tk
from app import main as app_main
from ui import AppUI

if __name__ == '__main__':
    queue = mp.Queue(maxsize=1000)
    camera_queue = mp.Queue(maxsize=10)
    app_process = mp.Process(target=app_main, args=(queue, camera_queue))
    root = tk.Tk()
    app_ui = AppUI(root, queue, camera_queue, app_process)
    try:
        app_process.start()
        root.mainloop()
    except KeyboardInterrupt:
        print("Terminating process...")
        app_process.terminate()